"""
DashboardTabWidget
Tab Dashboard với 4 biểu đồ đánh giá mô hình ML
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QFrame, QLabel, QScrollArea, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')  # PyQt6 compatible backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
from matplotlib.ticker import FuncFormatter
import numpy as np

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.evaluation import (
    load_evaluation_data,
    plot_feature_importance,
    plot_confusion_matrix,
    plot_roc_curves,
    plot_risk_distribution
)


class MatplotlibCanvas(FigureCanvas):
    """Canvas cho matplotlib plot trong PyQt6"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(320)
        try:
            self.setMinimumWidth(480)
        except Exception:
            pass


class DashboardTabWidget(QWidget):
    """
    Widget cho Tab Dashboard
    Hiển thị 4 biểu đồ trong layout 2x2:
    - Feature Importance
    - Confusion Matrix
    - ROC Curves
    - Risk Distribution
    """
    
    def __init__(self, user=None, query_service=None):
        super().__init__()
        self.user = user
        self.query_service = query_service
        self.eval_data = None
        self.kpi_cards = {}
        self.period_kind = 'month'
        self.period_count = 12
        self.health_labels = {}
        self.setup_ui()
        self.load_and_plot_data()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        root = QVBoxLayout(self)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        content = QWidget()
        main_layout = QVBoxLayout(content); main_layout.setContentsMargins(16,16,16,16); main_layout.setSpacing(16)
        
        # Refresh button (style như Secondary)
        self.btnRefresh = QPushButton("Làm mới Bảng điều khiển")
        try:
            self.btnRefresh.setObjectName('Secondary')
            self.btnRefresh.setStyleSheet("")
        except Exception:
            pass
        self.btnRefresh.clicked.connect(self.refresh_dashboard)

        kpi_row = QHBoxLayout(); kpi_row.setContentsMargins(0,0,0,0); kpi_row.setSpacing(16)
        def make_card(title_text: str, variant: str):
            card = QFrame(); card.setObjectName(variant)
            v = QVBoxLayout(card); v.setContentsMargins(16,16,16,16)
            try:
                card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            except Exception:
                pass
            t = QLabel(title_text); t.setObjectName('KpiTitle')
            val = QLabel('—'); val.setObjectName('KpiValue')
            v.addWidget(t)
            v.addWidget(val)
            return card, val
        card1, val1 = make_card('Tổng số dự báo', 'DashboardCardBlue')
        card2, val2 = make_card('Tỷ lệ High-Risk', 'DashboardCardRed')
        card3, val3 = make_card('Xác suất trung bình', 'DashboardCardYellow')
        self.kpi_cards = {'total': val1, 'high_rate': val2, 'avg_prob': val3}
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            kpi_row.addWidget(card1, 1)
            kpi_row.addWidget(card2, 1)
            kpi_row.addWidget(card3, 1)
            kpi_row.addWidget(self.btnRefresh)
            main_layout.addLayout(kpi_row)
        else:
            top_actions = QHBoxLayout(); top_actions.setContentsMargins(0,0,0,0); top_actions.addStretch(); top_actions.addWidget(self.btnRefresh)
            main_layout.addLayout(top_actions)
        # Admin dashboard không hiển thị thẻ "Model health" (đã có ở Báo Cáo)
        self.health_card = None
        
        # Grid layout 2x2 cho 4 biểu đồ
        self.main_grid = QGridLayout(); self.main_grid.setHorizontalSpacing(16); self.main_grid.setVerticalSpacing(16)
        
        # 4 canvas có thể tái sử dụng: admin (ML) hoặc user (vận hành)
        def make_chart(title_text: str, w: float = 7.0, h: float = 4.8):
            card = QFrame(); card.setObjectName('ChartCard')
            v = QVBoxLayout(card); v.setContentsMargins(12,12,12,12); v.setSpacing(8)
            t = QLabel(title_text); t.setObjectName('ChartTitle'); v.addWidget(t)
            canvas = MatplotlibCanvas(self, width=w, height=h); v.addWidget(canvas)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            v.setStretch(1, 1)
            return card, canvas, t

        card_tl, self.canvas_top_left, self.title_top_left = make_chart('Tỷ lệ theo risk bucket', 7.0, 5.0)
        card_tr, self.canvas_top_right, self.title_top_right = make_chart('Top 10 khách hàng theo nguy cơ', 7.0, 5.0)
        # Filter + Table inside the top-right card (User role only)
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            try:
                filter_row = QHBoxLayout(); filter_row.setSpacing(8)
                lbl = QLabel('Hiển thị:')
                self.top_filter_mode = QComboBox(); self.top_filter_mode.addItems(['Cao nhất', 'Thấp nhất'])
                filter_row.addWidget(lbl)
                filter_row.addWidget(self.top_filter_mode)
                card_tr.layout().insertLayout(1, filter_row)

                self.table_top_list = QTableWidget()
                self.table_top_list.setColumnCount(6)
                self.table_top_list.setHorizontalHeaderLabels(['Customer ID','Customer Name','ID Card','Probability','Risk','Label'])
                try:
                    hdr = self.table_top_list.horizontalHeader()
                    hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                    self.table_top_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                    self.table_top_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                    self.table_top_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                except Exception:
                    pass
                card_tr.layout().addWidget(self.table_top_list)
                card_tr.layout().setStretch(1, 0)
                card_tr.layout().setStretch(2, 0)
                card_tr.layout().setStretch(3, 1)
                self.top_filter_mode.currentTextChanged.connect(self._on_top_list_filter_changed)
            except Exception:
                pass
        
        card_bl, self.canvas_bottom_left, self.title_bottom_left = make_chart('Top 5 yếu tố ảnh hưởng', 7.0, 5.0)
        card_br, self.canvas_bottom_right, self.title_bottom_right = make_chart('Phân bổ khách hàng theo nhóm', 7.0, 5.0)

        self.card_tl = card_tl
        self.card_tr = card_tr
        self.card_bl = card_bl
        self.card_br = card_br
        if hasattr(self.user, 'is_admin') and self.user.is_admin():
            row_top = QHBoxLayout(); row_top.setContentsMargins(0,0,0,0); row_top.setSpacing(16)
            try:
                row_top.setAlignment(Qt.AlignmentFlag.AlignTop)
            except Exception:
                pass
            row_top.addWidget(self.card_tl, 5)
            row_top.addWidget(self.card_tr, 3)
            main_layout.addLayout(row_top)
            row_bottom = QHBoxLayout(); row_bottom.setContentsMargins(0,0,0,0); row_bottom.setSpacing(16)
            row_bottom.addWidget(self.card_bl, 1)
            row_bottom.addWidget(self.card_br, 1)
            main_layout.addLayout(row_bottom)
        else:
            self.main_grid.addWidget(self.card_tl, 0, 0)
            self.main_grid.addWidget(self.card_tr, 0, 1)
            self.main_grid.addWidget(self.card_bl, 1, 0)
            self.main_grid.addWidget(self.card_br, 1, 1)
            self.main_grid.setColumnStretch(0, 50)
            self.main_grid.setColumnStretch(1, 55)
            self.main_grid.setRowStretch(0, 1)
            self.main_grid.setRowStretch(1, 1)
            main_layout.addLayout(self.main_grid)
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            extra1 = QFrame(); extra1.setObjectName('ChartCard')
            v1 = QVBoxLayout(extra1); v1.setContentsMargins(12,12,12,12); v1.setSpacing(8)
            t1 = QLabel('Phân bố trạng thái thanh toán (PAY_0)'); t1.setObjectName('ChartTitle'); v1.addWidget(t1)
            self.canvas_pay_status = MatplotlibCanvas(self, width=6.5, height=4.2); v1.addWidget(self.canvas_pay_status)

            extra2 = QFrame(); extra2.setObjectName('ChartCard')
            v2 = QVBoxLayout(extra2); v2.setContentsMargins(12,12,12,12); v2.setSpacing(8)
            t2 = QLabel('Danh sách khách hàng trễ hạn gần đây'); t2.setObjectName('ChartTitle'); v2.addWidget(t2)
            self.table_late_customers = QTableWidget(0, 5)
            self.table_late_customers.setHorizontalHeaderLabels(['Khách hàng','CMND','Rủi ro','Số tháng trễ','Số tiền quá hạn'])
            try:
                hdr2 = self.table_late_customers.horizontalHeader()
                hdr2.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                self.table_late_customers.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.table_late_customers.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.table_late_customers.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            except Exception:
                pass
            v2.addWidget(self.table_late_customers)
            self.extra1 = extra1
            self.extra2 = extra2
            self.main_grid.addWidget(self.extra1, 2, 0)
            self.main_grid.addWidget(self.extra2, 2, 1)
            self.main_grid.setRowStretch(2, 1)

        main_layout.addStretch(1)
        self.scroll.setWidget(content)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        root.addWidget(self.scroll)
        # Bố cục cố định 2 cột 3 hàng với tỷ lệ 50:55

    def _apply_responsive_layout(self):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
    def load_and_plot_data(self):
        """Hiển thị dashboard theo role"""
        try:
            if hasattr(self.user, 'is_admin') and self.user.is_admin():
                # Admin: giữ dashboard ML hiện tại
                self.eval_data = load_evaluation_data()
                try:
                    self.title_top_left.setText('Tầm quan trọng đặc trưng')
                    self.title_top_right.setText('Ma trận nhầm lẫn')
                    self.title_bottom_left.setText('Đường cong ROC')
                    self.title_bottom_right.setText('Phân phối rủi ro')
                except Exception:
                    pass
                self._plot_admin_ml_dashboard()
            else:
                # User: dashboard vận hành
                try:
                    self.title_top_left.setText('Tỷ lệ theo risk bucket')
                    self.title_top_right.setText('Top 10 khách hàng theo nguy cơ')
                    self.title_bottom_left.setText('Top 5 yếu tố ảnh hưởng')
                    self.title_bottom_right.setText('Phân bổ khách hàng theo nhóm')
                except Exception:
                    pass
                self._plot_user_operational_dashboard()
                self._update_kpi_cards()
            print("✓ Dashboard loaded successfully")
        except Exception as e:
            print(f"⚠ Lỗi load dashboard: {e}")

    # ===================== Admin ML Dashboard =====================
    def _plot_admin_ml_dashboard(self):
        try:
            # Feature Importance
            ax = self.canvas_top_left.axes; ax.clear()
            feature_importance = self.eval_data.get('feature_importance', {})
            plot_feature_importance(ax, feature_importance, top_n=10)
            self.canvas_top_left.draw()

            # Confusion Matrix
            ax = self.canvas_top_right.axes; ax.clear()
            confusion_matrices = self.eval_data.get('confusion_matrices', {})
            cm = confusion_matrices.get('XGBoost')
            if cm is not None:
                plot_confusion_matrix(ax, cm, model_name='XGBoost')
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.canvas_top_right.draw()

            # ROC Curves
            ax = self.canvas_bottom_left.axes; ax.clear()
            roc_data = self.eval_data.get('roc_data', {})
            if roc_data:
                plot_roc_curves(ax, roc_data)
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.canvas_bottom_left.draw()

            # Risk Distribution
            ax = self.canvas_bottom_right.axes; ax.clear()
            y_test = self.eval_data.get('y_test')
            predictions = self.eval_data.get('predictions', {})
            if y_test is not None and len(y_test) > 0 and predictions:
                plot_risk_distribution(ax, y_test, predictions)
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.canvas_bottom_right.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ admin dashboard: {e}")

    # ===================== User Operational Dashboard =====================
    def _plot_user_operational_dashboard(self):
        # 1. Risk buckets
        try:
            ax = self.canvas_top_left.axes; ax.clear()
            since = self._compute_since_iso(self.period_kind, self.period_count)
            buckets = self._get_risk_bucket_counts(since)
            labels = ['0–20%', '20–40%', '40–60%', '60–80%', '80–100%']
            values = [buckets.get('0_20', 0), buckets.get('20_40', 0), buckets.get('40_60', 0), buckets.get('60_80', 0), buckets.get('80_100', 0)]
            colors = self._assign_rank_colors(values)
            bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1)
            try:
                max_v = max(values) if values else 0
                if max_v > 0:
                    ax.set_ylim(0, max_v * 1.25)
            except Exception:
                pass
            ax.set_ylabel('Số lượng khách hàng')
            ax.grid(axis='y', alpha=0.3)
            for bar in bars:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=9)
            self.canvas_top_left.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ risk buckets: {e}")

        # 2. Trend theo thời gian
        try:
            self._populate_top_list()
        except Exception as e:
            print(f"⚠ Lỗi vẽ top list: {e}")

        # 3. SHAP-lite Top 5 yếu tố (lọc theo thời gian)
        try:
            ax = self.canvas_bottom_left.axes; ax.clear()
            since = self._compute_since_iso(self.period_kind, self.period_count)
            shap = self._get_shap_lite_features(since)
            items = sorted(shap.items(), key=lambda kv: kv[1], reverse=True)[:5]
            features = [k for k,_ in items]
            scores = [v for _,v in items]
            shap_colors = ['#2F80ED','#F2994A','#27AE60','#EB5757','#EB5757']
            features_display = [('Tình trạng\nhôn nhân' if k == 'Tình trạng hôn nhân' else k) for k in features]
            ax.barh(features_display, scores, color=shap_colors[:len(scores)])
            ax.set_xlabel('Tầm ảnh hưởng (proxy)', labelpad=6)
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)
            try:
                try:
                    self.canvas_bottom_left.figure.set_layout_engine(None)
                except Exception:
                    pass
                self.canvas_bottom_left.figure.subplots_adjust(bottom=0.28)
            except Exception:
                pass
            self.canvas_bottom_left.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ SHAP-lite: {e}")

        # 4. Pie charts: Gender, Marriage, Education
        try:
            fig = self.canvas_bottom_right.figure
            fig.clear()
            gs = fig.add_gridspec(1, 3)
            ax1 = fig.add_subplot(gs[0,0])
            ax2 = fig.add_subplot(gs[0,1])
            ax3 = fig.add_subplot(gs[0,2])
            since = self._compute_since_iso(self.period_kind, self.period_count)
            gender, marriage, education = self._get_demographics_counts(since)
            def pie(ax, data, title):
                labels = [str(k) for k in data.keys()]
                sizes = [int(v) for v in data.values()]
                if sum(sizes)==0:
                    ax.text(0.5,0.5,'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
                    return
                colors = self._assign_rank_colors(sizes)
                ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, colors=colors, textprops={'fontsize':8})
                ax.axis('equal')
            pie(ax1, gender, 'Giới tính')
            pie(ax2, marriage, 'Tình trạng hôn nhân')
            pie(ax3, education, 'Trình độ học vấn')
            self.canvas_bottom_right.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ pie charts: {e}")

        # 5. Payment status distribution (PAY_0)
        try:
            ax = self.canvas_pay_status.axes; ax.clear()
            dist = self.query_service.get_payment_status_distribution() if self.query_service else {}
            labels = list(dist.keys())
            values = [int(dist[k]) for k in labels] if dist else []
            if values:
                ax.bar(labels, values, color='#F2994A')
                ax.set_ylabel('Số lượng')
                ax.grid(axis='y', alpha=0.3)
                try:
                    try:
                        self.canvas_pay_status.figure.set_layout_engine(None)
                    except Exception:
                        pass
                    self.canvas_pay_status.figure.subplots_adjust(bottom=0.25)
                except Exception:
                    pass
            else:
                ax.text(0.5,0.5,'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.canvas_pay_status.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ payment status: {e}")

        # 6. Late customers table (from DB)
        try:
            rows = self.query_service.get_top_late_customers_with_risk(limit=20) if self.query_service else []
            self.table_late_customers.setRowCount(len(rows))
            for i, r in enumerate(rows):
                vals = [r.get('customer_name'), r.get('customer_id_card'), r.get('risk'), r.get('months_late'), f"{r.get('amount_overdue',0.0):,.0f}"]
                for j, v in enumerate(vals):
                    self.table_late_customers.setItem(i, j, QTableWidgetItem(str(v)))
            self.table_late_customers.resizeColumnsToContents()
        except Exception as e:
            print(f"⚠ Lỗi vẽ bảng late customers: {e}")
    
    def plot_feature_importance_chart(self):
        """Vẽ biểu đồ Feature Importance"""
        try:
            ax = self.canvas_feature_importance.axes
            ax.clear()
            
            feature_importance = self.eval_data.get('feature_importance', {})
            plot_feature_importance(ax, feature_importance, top_n=10)
            
            self.canvas_feature_importance.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Feature Importance: {e}")
    
    def plot_confusion_matrix_chart(self):
        """Vẽ biểu đồ Confusion Matrix"""
        try:
            ax = self.canvas_confusion_matrix.axes
            ax.clear()
            
            confusion_matrices = self.eval_data.get('confusion_matrices', {})
            # Lấy confusion matrix của XGBoost (model chính)
            cm = confusion_matrices.get('XGBoost')
            
            if cm is not None:
                plot_confusion_matrix(ax, cm, model_name='XGBoost')
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu', 
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_confusion_matrix.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Confusion Matrix: {e}")
    
    def plot_roc_curves_chart(self):
        """Vẽ biểu đồ ROC Curves"""
        try:
            ax = self.canvas_roc.axes
            ax.clear()
            
            roc_data = self.eval_data.get('roc_data', {})
            
            if roc_data:
                plot_roc_curves(ax, roc_data)
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu',
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_roc.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ ROC Curves: {e}")
    
    def plot_risk_distribution_chart(self):
        """Vẽ biểu đồ Risk Distribution"""
        try:
            ax = self.canvas_risk_dist.axes
            ax.clear()
            
            y_test = self.eval_data.get('y_test')
            predictions = self.eval_data.get('predictions', {})
            
            if y_test is not None and len(y_test) > 0 and predictions:
                plot_risk_distribution(ax, y_test, predictions)
            else:
                ax.text(0.5, 0.5, 'Không có dữ liệu',
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_risk_dist.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Risk Distribution: {e}")
    
    def refresh_dashboard(self):
        """Refresh toàn bộ dashboard"""
        print("🔄 Refreshing dashboard...")
        self.load_and_plot_data()

    def _on_top_list_filter_changed(self, _=None):
        try:
            self._populate_top_list()
        except Exception:
            pass

    def _populate_top_list(self):
        # Show table and hide canvas in this card
        try:
            self.canvas_top_right.setVisible(False)
        except Exception:
            pass
        try:
            self.table_top_list.setVisible(True)
        except Exception:
            pass
        mode = 'Cao nhất'
        try:
            mode = self.top_filter_mode.currentText()
        except Exception:
            pass
        # Fetch latest-day predictions joined with customers
        rows = []
        if self.query_service and hasattr(self.query_service, 'get_top_predictions_join_customers'):
            try:
                asc = (mode == 'Thấp nhất')
                rows = self.query_service.get_top_predictions_join_customers(limit=10, ascending=asc)
            except Exception:
                rows = []
        # Fallback demo
        if not rows:
            rows = [
                {'customer_id': i+1, 'customer_name': f'Customer {i+1}', 'customer_id_card': f'ID{i+1:05d}',
                 'probability': max(0.0, min(1.0, 0.8 - i*0.03)), 'label': 1 if i%3==0 else 0}
                for i in range(20)
            ]
        # Ensure exactly 10 items
        rows = rows[:10]
        # Populate table
        self.table_top_list.setRowCount(len(rows))
        for i, r in enumerate(rows):
            prob = float(r.get('probability',0.0))
            vals = [
                r.get('customer_id'),
                r.get('customer_name') or '—',
                r.get('customer_id_card') or '—',
                f"{prob*100:.1f}%",
                self._risk_label_from_probability(prob),
                r.get('label'),
            ]
            for j, v in enumerate(vals):
                self.table_top_list.setItem(i, j, QTableWidgetItem(str(v)))
        try:
            self.table_top_list.resizeColumnsToContents()
        except Exception:
            pass
        try:
            self.title_top_right.setText('Top 10 khách hàng theo nguy cơ')
        except Exception:
            pass

    def _risk_label_from_probability(self, p: float) -> str:
        try:
            if p < 0.20:
                return 'Nguy cơ rất thấp'
            if p < 0.40:
                return 'Nguy cơ thấp'
            if p < 0.60:
                return 'Nguy cơ trung bình'
            if p < 0.80:
                return 'Nguy cơ cao'
            return 'Nguy cơ rất cao'
        except Exception:
            return 'Nguy cơ N/A'

    # period filters removed

    # ===================== Data aggregation helpers =====================
    def _update_health_card(self):
        if not self.health_labels:
            return
        try:
            # Default rate / high-risk drift depending on period
            series = []
            if self.period_kind == 'quarter':
                series = self._get_quarterly_high_risk_rate(self.period_count)
            else:
                series = self._get_monthly_default_rate(self.period_count)
            delta = 0.0
            if series and len(series) >= 2:
                delta = (series[-1]['rate'] - series[-2]['rate']) * 100
            status = 'Cảnh báo' if abs(delta) >= 5.0 else 'Ổn định'
            self.health_labels['data']['desc'].setText(f"Độ lệch tỷ lệ vỡ nợ: {delta:+.1f}%")
            self.health_labels['data']['chip'].setText(status)
            self.health_labels['data']['chip'].setObjectName('ChipWarning' if status=='Cảnh báo' else 'ChipStable')
            try:
                self.health_labels['data']['chip'].setStyleSheet("")
            except Exception:
                pass

            # Prediction drift via avg probability (approx)
            if self.query_service and hasattr(self.query_service, 'get_prediction_stats'):
                cur = self.query_service.get_prediction_stats()
                avg_prob = float(cur.get('avg_probability', 0.0))
                prev_series = self._get_monthly_default_rate(2)
                prev_rate = prev_series[-2]['rate'] if len(prev_series) >= 2 else avg_prob
                pred_delta = (avg_prob - prev_rate) * 100
                pstatus = 'Cảnh báo' if abs(pred_delta) >= 5.0 else 'Ổn định'
                self.health_labels['pred']['desc'].setText(f"Độ lệch dự báo: {pred_delta:+.1f}%")
                self.health_labels['pred']['chip'].setText(pstatus)
                self.health_labels['pred']['chip'].setObjectName('ChipWarning' if pstatus=='Cảnh báo' else 'ChipStable')
                try:
                    self.health_labels['pred']['chip'].setStyleSheet("")
                except Exception:
                    pass
            else:
                self.health_labels['pred']['desc'].setText("Độ lệch dự báo: N/A")
                self.health_labels['pred']['chip'].setText("")

            # Feature drift (proxy: high-risk change)
            quarters = self._get_quarterly_high_risk_rate(2)
            feat_delta = (quarters[-1]['rate'] - quarters[-2]['rate']) * 100 if len(quarters) >= 2 else 0.0
            fstatus = 'Cảnh báo' if abs(feat_delta) >= 10.0 else 'Ổn định'
            self.health_labels['feat']['desc'].setText(f"Độ lệch PAY_0: {feat_delta:+.1f}%")
            self.health_labels['feat']['chip'].setText(fstatus)
            self.health_labels['feat']['chip'].setObjectName('ChipWarning' if fstatus=='Cảnh báo' else 'ChipStable')
            try:
                self.health_labels['feat']['chip'].setStyleSheet("")
            except Exception:
                pass

            # Model accuracy (placeholder)
            acc_pct = None
            try:
                y_test = self.eval_data.get('y_test') if self.eval_data else None
                preds_dict = self.eval_data.get('predictions', {}) if self.eval_data else {}
                preds = preds_dict.get('XGBoost', None)
                if preds is None and preds_dict:
                    first_key = next(iter(preds_dict))
                    preds = preds_dict.get(first_key)
                if y_test is not None and preds is not None and len(y_test) == len(preds):
                    labels = (np.array(preds) >= 0.5).astype(int)
                    acc_pct = float((labels == np.array(y_test)).mean()) * 100.0
            except Exception:
                acc_pct = None
            if acc_pct is not None:
                self.health_labels['acc']['desc'].setText(f"Độ chính xác mô hình: {acc_pct:.1f}%")
                astatus = 'Ổn định' if acc_pct >= 75.0 else 'Cảnh báo'
                self.health_labels['acc']['chip'].setText(astatus)
                self.health_labels['acc']['chip'].setObjectName('ChipStable' if astatus=='Ổn định' else 'ChipWarning')
            else:
                self.health_labels['acc']['desc'].setText("Độ chính xác mô hình: N/A")
                self.health_labels['acc']['chip'].setText("")
            try:
                self.health_labels['acc']['chip'].setStyleSheet("")
            except Exception:
                pass
        except Exception:
            self.health_labels['data']['desc'].setText(f"Độ lệch tỷ lệ vỡ nợ: N/A")
            self.health_labels['pred']['desc'].setText(f"Độ lệch dự báo: N/A")
            self.health_labels['feat']['desc'].setText(f"Độ lệch đặc trưng: N/A")
            self.health_labels['acc']['desc'].setText("Độ chính xác mô hình: N/A")
    def _update_kpi_cards(self):
        stats = None
        if self.query_service and hasattr(self.query_service, 'get_prediction_stats'):
            try:
                stats = self.query_service.get_prediction_stats()
            except Exception:
                stats = None
        if not stats:
            buckets = self._get_risk_bucket_counts()
            total = sum([buckets.get(k,0) for k in ['0_20','20_40','40_60','60_80','80_100']])
            high = buckets.get('60_80',0) + buckets.get('80_100',0)
            avg = 0.0
            stats = {'total_predictions': total, 'high_risk_count': high, 'avg_probability': avg}
        if self.kpi_cards:
            self.kpi_cards['total'].setText(f"{stats.get('total_predictions',0):,}")
            total = max(stats.get('total_predictions',1), 1)
            high_rate = stats.get('high_risk_count',0)/total
            self.kpi_cards['high_rate'].setText(f"{high_rate*100:.1f}%")
            self.kpi_cards['avg_prob'].setText(f"{stats.get('avg_probability',0.0)*100:.1f}%")

    def _get_risk_bucket_counts(self, since_iso: str | None = None):
        if self.query_service:
            try:
                if since_iso and hasattr(self.query_service, 'get_risk_bucket_counts_since'):
                    return self.query_service.get_risk_bucket_counts_since(since_iso)
                return self.query_service.get_risk_bucket_counts()
            except Exception:
                pass
        # Fallback demo
        return {'0_20': 12, '20_40': 34, '40_60': 28, '60_80': 18, '80_100': 8}

    def _get_monthly_default_rate(self, months: int = 12):
        if self.query_service:
            try:
                return self.query_service.get_monthly_default_rate(months)
            except Exception:
                pass
        # Fallback demo
        return [{'period': f'2025-{str(m).zfill(2)}', 'rate': 0.12 + (m%3)*0.02} for m in range(1,7)]

    def _get_monthly_default_rate_recent(self, months: int = 12):
        if self.query_service and hasattr(self.query_service, 'get_monthly_default_rate_recent'):
            try:
                return self.query_service.get_monthly_default_rate_recent(months)
            except Exception:
                pass
        return []

    def _get_quarterly_high_risk_rate(self, quarters: int = 8):
        if self.query_service:
            try:
                return self.query_service.get_quarterly_high_risk_rate(quarters)
            except Exception:
                pass
        # Fallback demo
        return [{'period': f'2025-Q{q}', 'rate': 0.22 + (q%2)*0.03} for q in range(1,5)]

    def _get_quarterly_high_risk_rate_recent(self, quarters: int = 8):
        if self.query_service and hasattr(self.query_service, 'get_quarterly_high_risk_rate_recent'):
            try:
                return self.query_service.get_quarterly_high_risk_rate_recent(quarters)
            except Exception:
                pass
        return []
    def _get_demographics_counts(self, since_iso: str | None = None):
        if self.query_service:
            try:
                if since_iso and hasattr(self.query_service, 'get_demographics_counts_since'):
                    return self.query_service.get_demographics_counts_since(since_iso)
                return self.query_service.get_demographics_counts()
            except Exception:
                pass
        # Fallback demo
        return (
            {'Nam': 60, 'Nữ': 40},
            {'Độc thân': 55, 'Kết hôn': 35, 'Khác': 10},
            {'Trung học': 40, 'Đại học': 45, 'Cao học': 15}
        )

    def _get_shap_lite_features(self, since_iso: str | None = None):
        if self.query_service and since_iso and hasattr(self.query_service, 'get_shap_lite_importance_since'):
            try:
                return self.query_service.get_shap_lite_importance_since(since_iso)
            except Exception:
                pass
        # Fallback demo scores
        return {'PAY_0': 0.25, 'PAY_2': 0.15, 'LIMIT_BAL': 0.12, 'Tình trạng hôn nhân': 0.03, 'Tuổi': 0.06}

    def _assign_rank_colors(self, values):
        if not values:
            return ['#EB5757']
        idxs = list(range(len(values)))
        idxs.sort(key=lambda i: values[i], reverse=True)
        colors = ['#EB5757']*len(values)
        if len(idxs) >= 1:
            colors[idxs[0]] = '#2F80ED'
        if len(idxs) >= 2:
            colors[idxs[1]] = '#F2994A'
        if len(idxs) >= 3:
            colors[idxs[2]] = '#27AE60'
        return colors
    def _get_weekly_default_rate(self, weeks: int = 8):
        if self.query_service and hasattr(self.query_service, 'get_weekly_default_rate'):
            try:
                return self.query_service.get_weekly_default_rate(weeks)
            except Exception:
                pass
        # Fallback demo
        return [{'period': f'2025-W{str(w).zfill(2)}', 'rate': 0.05 + (w%3)*0.01} for w in range(1, weeks+1)]

    def _compute_since_iso(self, kind: str, count: int) -> str:
        from datetime import datetime, timedelta
        now = datetime.now()
        if kind == 'week':
            since = now - timedelta(days=7*count)
        else:
            # months/quarters
            months = count if kind == 'month' else count*3
            y = now.year; m = now.month
            for _ in range(months):
                m -= 1
                if m == 0:
                    m = 12; y -= 1
            since = now.replace(year=y, month=m, day=1)
        return since.strftime('%Y-%m-%d')
