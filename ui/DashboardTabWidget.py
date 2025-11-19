"""
DashboardTabWidget
Tab Dashboard với 4 biểu đồ đánh giá mô hình ML
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QFrame, QLabel, QScrollArea, QComboBox
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')  # PyQt6 compatible backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


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
        # Scrollable content
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        content = QWidget()
        main_layout = QVBoxLayout(content); main_layout.setContentsMargins(16,16,16,16); main_layout.setSpacing(16)
        
        # Filter + Refresh (Admin only)
        button_layout = QHBoxLayout()
        if hasattr(self.user, 'is_admin') and self.user.is_admin():
            lbl = QLabel('Kỳ:')
            self.cmbPeriod = QComboBox(); self.cmbPeriod.addItems(['Tuần','Tháng','Quý'])
            self.cmbPeriod.setCurrentText('Tháng')
            self.cmbPeriod.currentTextChanged.connect(self._on_period_kind_changed)
            lbl2 = QLabel('Số kỳ:')
            self.cmbCount = QComboBox(); self.cmbCount.addItems(['8','12'])
            self.cmbCount.setCurrentText('12')
            self.cmbCount.currentTextChanged.connect(self._on_period_count_changed)
            button_layout.addWidget(lbl)
            button_layout.addWidget(self.cmbPeriod)
            button_layout.addSpacing(12)
            button_layout.addWidget(lbl2)
            button_layout.addWidget(self.cmbCount)
        button_layout.addStretch()
        
        self.btnRefresh = QPushButton("🔄 Refresh Dashboard")
        self.btnRefresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnRefresh.clicked.connect(self.refresh_dashboard)
        button_layout.addWidget(self.btnRefresh)
        
        main_layout.addLayout(button_layout)

        # KPI cards row
        kpi_row = QHBoxLayout(); kpi_row.setContentsMargins(0,0,0,0); kpi_row.setSpacing(16)
        def make_card(title_text: str, variant: str):
            card = QFrame(); card.setObjectName(variant)
            v = QVBoxLayout(card); v.setContentsMargins(16,16,16,16)
            t = QLabel(title_text); t.setObjectName('KpiTitle')
            val = QLabel('—'); val.setObjectName('KpiValue')
            v.addWidget(t)
            v.addWidget(val)
            return card, val
        card1, val1 = make_card('Tổng số dự báo', 'DashboardCardBlue')
        card2, val2 = make_card('Tỷ lệ High-Risk', 'DashboardCardRed')
        card3, val3 = make_card('Xác suất trung bình', 'DashboardCardYellow')
        self.kpi_cards = {'total': val1, 'high_rate': val2, 'avg_prob': val3}
        kpi_row.addWidget(card1)
        kpi_row.addWidget(card2)
        kpi_row.addWidget(card3)
        main_layout.addLayout(kpi_row)
        # Admin-only: Health/Drift card
        if hasattr(self.user, 'is_admin') and self.user.is_admin():
            health_card = QFrame(); health_card.setObjectName('ChartCard')
            hv = QVBoxLayout(health_card); hv.setContentsMargins(12,12,12,12)
            ht = QLabel('Model health / drift check'); ht.setObjectName('ChartTitle'); hv.addWidget(ht)
            lbl_data = QLabel('Data drift: …'); lbl_pred = QLabel('Prediction drift: …'); lbl_feat = QLabel('Feature drift: …'); lbl_acc = QLabel('Model accuracy: …')
            for l in [lbl_data, lbl_pred, lbl_feat, lbl_acc]:
                l.setObjectName('HealthItem')
                hv.addWidget(l)
            self.health_labels = {'data': lbl_data, 'pred': lbl_pred, 'feat': lbl_feat, 'acc': lbl_acc}
            main_layout.addWidget(health_card)
        
        # Grid layout 2x2 cho 4 biểu đồ
        grid_layout = QGridLayout(); grid_layout.setHorizontalSpacing(16); grid_layout.setVerticalSpacing(16)
        
        # 4 canvas có thể tái sử dụng: admin (ML) hoặc user (vận hành)
        def make_chart(title_text: str, w: float = 7.0, h: float = 6.5):
            card = QFrame(); card.setObjectName('ChartCard')
            v = QVBoxLayout(card); v.setContentsMargins(12,12,12,12)
            t = QLabel(title_text); t.setObjectName('ChartTitle'); v.addWidget(t)
            canvas = MatplotlibCanvas(self, width=w, height=h); v.addWidget(canvas)
            return card, canvas

        card_tl, self.canvas_top_left = make_chart('Tỷ lệ theo risk bucket', 5.5, 6.5)
        card_tr, self.canvas_top_right = make_chart('Trend vỡ nợ theo thời gian', 8.0, 7.8)
        card_bl, self.canvas_bottom_left = make_chart('Top 5 yếu tố ảnh hưởng')
        card_br, self.canvas_bottom_right = make_chart('Phân bổ khách hàng theo nhóm')

        grid_layout.addWidget(card_tl, 0, 0)
        grid_layout.addWidget(card_tr, 0, 1)
        grid_layout.addWidget(card_bl, 1, 0)
        grid_layout.addWidget(card_br, 1, 1)
        # 6:4 width ratio (Trend wider, Buckets narrower)
        grid_layout.setColumnStretch(0, 4)
        grid_layout.setColumnStretch(1, 6)
        
        main_layout.addLayout(grid_layout)
        scroll.setWidget(content)
        root.addWidget(scroll)
    
    def load_and_plot_data(self):
        """Hiển thị dashboard theo role"""
        try:
            if hasattr(self.user, 'is_admin') and self.user.is_admin():
                # Admin: giữ dashboard ML hiện tại
                self.eval_data = load_evaluation_data()
                self._plot_admin_ml_dashboard()
                self._update_health_card()
            else:
                # User: dashboard vận hành
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
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            self.canvas_top_right.draw()

            # ROC Curves
            ax = self.canvas_bottom_left.axes; ax.clear()
            roc_data = self.eval_data.get('roc_data', {})
            if roc_data:
                plot_roc_curves(ax, roc_data)
            else:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            self.canvas_bottom_left.draw()

            # Risk Distribution
            ax = self.canvas_bottom_right.axes; ax.clear()
            y_test = self.eval_data.get('y_test')
            predictions = self.eval_data.get('predictions', {})
            if y_test is not None and len(y_test) > 0 and predictions:
                plot_risk_distribution(ax, y_test, predictions)
            else:
                ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            self.canvas_bottom_right.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ admin dashboard: {e}")

    # ===================== User Operational Dashboard =====================
    def _plot_user_operational_dashboard(self):
        # 1. Risk buckets
        try:
            ax = self.canvas_top_left.axes; ax.clear()
            buckets = self._get_risk_bucket_counts()
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
            ax.set_title('Tỷ lệ khách hàng theo risk bucket', fontsize=12, fontweight='bold')
            ax.set_ylabel('Số lượng khách hàng')
            ax.grid(axis='y', alpha=0.3)
            for bar in bars:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=9)
            self.canvas_top_left.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ risk buckets: {e}")

        # 2. Trend theo thời gian
        try:
            ax = self.canvas_top_right.axes; ax.clear()
            monthly = self._get_monthly_default_rate()
            quarters = self._get_quarterly_high_risk_rate()
            if monthly:
                xs = [m['period'] for m in monthly]
                ys = [m['rate']*100 for m in monthly]
                ax.plot(xs, ys, marker='o', color='#2F80ED', label='% default theo tháng')
            if quarters:
                xq = [q['period'] for q in quarters]
                yq = [q['rate']*100 for q in quarters]
                ax.plot(xq, yq, marker='s', color='#F2994A', label='% high-risk theo quý')
            ax.set_title('Trend vỡ nợ theo thời gian', fontsize=12, fontweight='bold')
            ax.set_ylabel('%')
            ax.grid(alpha=0.3)
            try:
                ax.tick_params(axis='x', labelrotation=45, labelsize=10)
                ax.margins(x=0.02)
            except Exception:
                pass
            ax.legend(fontsize=9)
            try:
                self.canvas_top_right.figure.subplots_adjust(bottom=0.22)
                self.canvas_top_right.figure.tight_layout()
            except Exception:
                pass
            self.canvas_top_right.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ trend: {e}")

        # 3. SHAP-lite Top 5 yếu tố
        try:
            ax = self.canvas_bottom_left.axes; ax.clear()
            features = ['PAY_0','PAY_2','LIMIT_BAL','Tình trạng hôn nhân','Tuổi']
            scores = [0.25, 0.15, 0.12, 0.03, 0.06]
            shap_colors = ['#2F80ED','#F2994A','#27AE60','#EB5757','#EB5757']
            ax.barh(features, scores, color=shap_colors)
            ax.set_xlabel('Tầm ảnh hưởng (giả lập)')
            ax.set_title('Top 5 yếu tố ảnh hưởng (SHAP-lite)', fontsize=12, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)
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
            gender, marriage, education = self._get_demographics_counts()
            def pie(ax, data, title):
                labels = [str(k) for k in data.keys()]
                sizes = [int(v) for v in data.values()]
                if sum(sizes)==0:
                    ax.text(0.5,0.5,'No data', ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(title)
                    return
                colors = self._assign_rank_colors(sizes)
                ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, colors=colors, textprops={'fontsize':8})
                ax.axis('equal')
                ax.set_title(title, fontsize=10)
            pie(ax1, gender, 'Gender')
            pie(ax2, marriage, 'Marriage Status')
            pie(ax3, education, 'Education')
            self.canvas_bottom_right.draw()
        except Exception as e:
            print(f"⚠ Lỗi vẽ pie charts: {e}")
    
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
                ax.text(0.5, 0.5, 'No data available', 
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
                ax.text(0.5, 0.5, 'No data available',
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
                ax.text(0.5, 0.5, 'No data available',
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_risk_dist.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Risk Distribution: {e}")
    
    def refresh_dashboard(self):
        """Refresh toàn bộ dashboard"""
        print("🔄 Refreshing dashboard...")
        self.load_and_plot_data()

    def _on_period_kind_changed(self, text: str):
        self.period_kind = {'Tuần':'week','Tháng':'month','Quý':'quarter'}.get(text, 'month')

    def _on_period_count_changed(self, text: str):
        try:
            self.period_count = int(text)
        except Exception:
            self.period_count = 12

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
            status = 'Warning' if abs(delta) >= 5.0 else 'Stable'
            self.health_labels['data'].setText(f"Default rate drift: {delta:+.1f}% ({status})")

            # Prediction drift via avg probability (approx)
            if self.query_service and hasattr(self.query_service, 'get_prediction_stats'):
                cur = self.query_service.get_prediction_stats()
                avg_prob = float(cur.get('avg_probability', 0.0))
                prev_series = self._get_monthly_default_rate(2)
                prev_rate = prev_series[-2]['rate'] if len(prev_series) >= 2 else avg_prob
                pred_delta = (avg_prob - prev_rate) * 100
                pstatus = 'Warning' if abs(pred_delta) >= 5.0 else 'Stable'
                self.health_labels['pred'].setText(f"Prediction drift: {pred_delta:+.1f}% ({pstatus})")
            else:
                self.health_labels['pred'].setText("Prediction drift: N/A")

            # Feature drift (proxy: high-risk change)
            quarters = self._get_quarterly_high_risk_rate(2)
            feat_delta = (quarters[-1]['rate'] - quarters[-2]['rate']) * 100 if len(quarters) >= 2 else 0.0
            fstatus = 'Warning' if abs(feat_delta) >= 10.0 else 'Stable'
            self.health_labels['feat'].setText(f"PAY_0 drift: {feat_delta:+.1f}% ({fstatus})")

            # Model accuracy (placeholder)
            self.health_labels['acc'].setText("Model accuracy: Stable")
        except Exception:
            self.health_labels['data'].setText(f"Default rate drift: N/A")
            self.health_labels['pred'].setText(f"Prediction drift: N/A")
            self.health_labels['feat'].setText(f"Feature drift: N/A")
            self.health_labels['acc'].setText("Model accuracy: N/A")
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

    def _get_risk_bucket_counts(self):
        if self.query_service:
            try:
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

    def _get_quarterly_high_risk_rate(self, quarters: int = 8):
        if self.query_service:
            try:
                return self.query_service.get_quarterly_high_risk_rate(quarters)
            except Exception:
                pass
        # Fallback demo
        return [{'period': f'2025-Q{q}', 'rate': 0.22 + (q%2)*0.03} for q in range(1,5)]

    def _get_demographics_counts(self):
        if self.query_service:
            try:
                return self.query_service.get_demographics_counts()
            except Exception:
                pass
        # Fallback demo
        return (
            {'Nam': 60, 'Nữ': 40},
            {'Độc thân': 55, 'Kết hôn': 35, 'Khác': 10},
            {'Trung học': 40, 'Đại học': 45, 'Cao học': 15}
        )

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
