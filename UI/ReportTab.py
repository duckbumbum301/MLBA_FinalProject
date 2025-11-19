from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QFrame, QHeaderView, QDateEdit, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .user_model import User
except Exception:
    from user_model import User
try:
    from .integration import get_db_connector, get_query_service
except Exception:
    from integration import get_db_connector, get_query_service
import json
try:
    from services.model_management_service import ModelManagementService
    _HaveModelMgmt = True
except Exception:
    ModelManagementService = None
    _HaveModelMgmt = False
try:
    from ml.evaluation import load_evaluation_data
except Exception:
    load_evaluation_data = None

class ReportTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.view_mode = 'own_data_only' if self.user.is_user() else 'all'
        self._model_labels = {}
        self.setup_ui()
        self.refresh_report()

    def setup_ui(self):
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(16,16,16,16); layout.setSpacing(16)
        
        # Filters + actions
        filters = QHBoxLayout()
        self.cmb_time = QComboBox(); self.cmb_time.addItems(['Hôm nay', 'Tuần này', 'Tháng này', 'Quý này', 'Năm nay', 'Tất cả'])
        self.cmb_status = QComboBox(); self.cmb_status.addItems(['Tất cả', 'Nguy cơ cao', 'Nguy cơ thấp'])
        self.btn_export_csv = QPushButton('Xuất CSV'); self.btn_export_csv.setObjectName('Secondary'); self.btn_export_csv.clicked.connect(self.export_csv)
        # Date range controls
        self.date_start = QDateEdit(); self.date_start.setCalendarPopup(True)
        self.date_end = QDateEdit(); self.date_end.setCalendarPopup(True)
        from PyQt6.QtCore import QDate
        today = QDate.currentDate(); first_day = QDate(today.year(), today.month(), 1)
        self.date_start.setDate(first_day); self.date_end.setDate(today)
        filters.addWidget(QLabel('Thời gian:')); filters.addWidget(self.cmb_time)
        filters.addWidget(QLabel('Trạng thái:')); filters.addWidget(self.cmb_status)
        filters.addWidget(QLabel('Từ ngày:')); filters.addWidget(self.date_start)
        filters.addWidget(QLabel('Đến ngày:')); filters.addWidget(self.date_end)
        filters.addStretch(); filters.addWidget(self.btn_export_csv)
        layout.addLayout(filters)
        self.cmb_time.currentIndexChanged.connect(self.refresh_report)
        self.cmb_status.currentIndexChanged.connect(self.refresh_report)
        self.cmb_time.currentTextChanged.connect(self.refresh_report)
        self.cmb_status.currentTextChanged.connect(self.refresh_report)
        self.date_start.dateChanged.connect(self.refresh_report)
        self.date_end.dateChanged.connect(self.refresh_report)

        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            kpi_card = QFrame(); kpi_card.setObjectName('Card'); kpi_box = QVBoxLayout(kpi_card)
            kpi_title = QLabel('Tổng quan hệ thống'); kpi_title.setObjectName('CardTitle'); kpi_box.addWidget(kpi_title)
            kpi = QHBoxLayout(); kpi_box.addLayout(kpi)
            self.lbl_total = QLabel('Tổng dự báo: -'); self.lbl_total.setObjectName('Heading3')
            self.lbl_high = QLabel('Nguy cơ cao: -'); self.lbl_high.setObjectName('Heading3')
            self.lbl_avg = QLabel('Xác suất TB: -'); self.lbl_avg.setObjectName('Heading3')
            kpi.addWidget(self.lbl_total); kpi.addWidget(self.lbl_high); kpi.addWidget(self.lbl_avg); kpi.addStretch()
            layout.addWidget(kpi_card)

            trend_card = QFrame(); trend_card.setObjectName('Card'); tlay = QVBoxLayout(trend_card)
            trend_title = QLabel('Tóm tắt xu hướng (báo cáo)'); trend_title.setObjectName('CardTitle'); tlay.addWidget(trend_title)
            self.tbl_monthly = QTableWidget(0, 2); self.tbl_monthly.setHorizontalHeaderLabels(['Tháng', 'Tỷ lệ vỡ nợ'])
            self.tbl_monthly.setAlternatingRowColors(True)
            self.tbl_monthly.horizontalHeader().setStretchLastSection(True)
            self.tbl_monthly.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.tbl_quarterly = QTableWidget(0, 2); self.tbl_quarterly.setHorizontalHeaderLabels(['Quý', 'Tỷ lệ high-risk'])
            self.tbl_quarterly.setAlternatingRowColors(True)
            self.tbl_quarterly.horizontalHeader().setStretchLastSection(True)
            self.tbl_quarterly.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            row_trend = QHBoxLayout(); row_trend.addWidget(self.tbl_monthly); row_trend.addWidget(self.tbl_quarterly)
            tlay.addLayout(row_trend)
            layout.addWidget(trend_card)

        # Segments summary
        seg_card = QFrame(); seg_card.setObjectName('Card'); seg_box = QVBoxLayout(seg_card)
        seg_title = QLabel('Phân khúc khách hàng'); seg_title.setObjectName('CardTitle'); seg_box.addWidget(seg_title)
        sg = QHBoxLayout(); seg_box.addLayout(sg)
        self.tbl_gender = QTableWidget(0, 2); self.tbl_gender.setHorizontalHeaderLabels(['Giới', 'Số lượng'])
        self.tbl_gender.setAlternatingRowColors(True)
        self.tbl_gender.horizontalHeader().setStretchLastSection(True)
        self.tbl_gender.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_marriage = QTableWidget(0, 2); self.tbl_marriage.setHorizontalHeaderLabels(['Hôn nhân', 'Số lượng'])
        self.tbl_marriage.setAlternatingRowColors(True)
        self.tbl_marriage.horizontalHeader().setStretchLastSection(True)
        self.tbl_marriage.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_edu = QTableWidget(0, 2); self.tbl_edu.setHorizontalHeaderLabels(['Học vấn', 'Số lượng'])
        self.tbl_edu.setAlternatingRowColors(True)
        self.tbl_edu.horizontalHeader().setStretchLastSection(True)
        self.tbl_edu.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sg.addWidget(self.tbl_gender); sg.addWidget(self.tbl_marriage); sg.addWidget(self.tbl_edu)
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            layout.addWidget(seg_card)

        # Top/Bottom customers
        top_card = QFrame(); top_card.setObjectName('Card'); top_box = QVBoxLayout(top_card)
        top_title = QLabel('Top/Bottom khách hàng theo xác suất'); top_title.setObjectName('CardTitle'); top_box.addWidget(top_title)
        tp = QHBoxLayout(); top_box.addLayout(tp)
        self.tbl_top = QTableWidget(0, 4); self.tbl_top.setHorizontalHeaderLabels(['Khách', 'CMND', 'Xác suất', 'Nhãn'])
        self.tbl_top.setAlternatingRowColors(True)
        self.tbl_top.horizontalHeader().setStretchLastSection(True)
        self.tbl_top.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_bottom = QTableWidget(0, 4); self.tbl_bottom.setHorizontalHeaderLabels(['Khách', 'CMND', 'Xác suất', 'Nhãn'])
        self.tbl_bottom.setAlternatingRowColors(True)
        self.tbl_bottom.horizontalHeader().setStretchLastSection(True)
        self.tbl_bottom.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tp.addWidget(self.tbl_top); tp.addWidget(self.tbl_bottom)
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            layout.addWidget(top_card)

        # Latest day predictions (detail)
        latest_card = QFrame(); latest_card.setObjectName('Card'); lt = QVBoxLayout(latest_card)
        latest_title = QLabel('Dự báo gần đây (theo bộ lọc)'); latest_title.setObjectName('CardTitle'); lt.addWidget(latest_title)
        self.tbl_latest = QTableWidget(0, 8)
        self.tbl_latest.setHorizontalHeaderLabels(['Khách', 'CMND', 'Xác suất', 'Nhãn', 'Hạn mức', 'Tuổi', 'PAY_0', 'BILL_AMT1'])
        self.tbl_latest.setAlternatingRowColors(True)
        self.tbl_latest.horizontalHeader().setStretchLastSection(True)
        self.tbl_latest.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lt.addWidget(self.tbl_latest)
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
            layout.addWidget(latest_card)

        # Info (role mode)
        self.info = QLabel(); self.info.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.info.setText('Chế độ: dữ liệu của tôi' if self.view_mode == 'own_data_only' else 'Chế độ: tất cả')
        layout.addWidget(self.info)

        model_card = QFrame(); model_card.setObjectName('Card')
        mv = QVBoxLayout(model_card); mv.setContentsMargins(16,16,16,16); mv.setSpacing(12)
        mt = QLabel('Hoạt động mô hình ML'); mt.setObjectName('SectionTitle'); mv.addWidget(mt)
        r1 = QHBoxLayout(); r1.setSpacing(8)
        l1 = QLabel('Mô hình đang hoạt động:'); v1 = QLabel('—'); r1.addWidget(l1); r1.addWidget(v1); r1.addStretch()
        r2 = QHBoxLayout(); r2.setSpacing(8)
        l2 = QLabel('Ngưỡng:'); v2 = QLabel('—'); r2.addWidget(l2); r2.addWidget(v2); r2.addStretch()
        r3 = QHBoxLayout(); r3.setSpacing(8)
        l3 = QLabel('AUC:'); v3 = QLabel('—'); r3.addWidget(l3); r3.addWidget(v3); r3.addStretch()
        r4 = QHBoxLayout(); r4.setSpacing(8)
        l4 = QLabel('Độ chính xác:'); v4 = QLabel('—'); r4.addWidget(l4); r4.addWidget(v4); r4.addStretch()
        r5 = QHBoxLayout(); r5.setSpacing(8)
        l5 = QLabel('F1-Score:'); v5 = QLabel('—'); r5.addWidget(l5); r5.addWidget(v5); r5.addStretch()
        r6 = QHBoxLayout(); r6.setSpacing(8)
        l6 = QLabel('Huấn luyện lúc:'); v6 = QLabel('—'); r6.addWidget(l6); r6.addWidget(v6); r6.addStretch()
        r7 = QHBoxLayout(); r7.setSpacing(8)
        l7 = QLabel('Huấn luyện bởi:'); v7 = QLabel('—'); r7.addWidget(l7); r7.addWidget(v7); r7.addStretch()
        mv.addLayout(r1); mv.addLayout(r2); mv.addLayout(r3); mv.addLayout(r4); mv.addLayout(r5); mv.addLayout(r6); mv.addLayout(r7)
        self._model_labels = {'name': v1, 'thr': v2, 'auc': v3, 'acc': v4, 'f1': v5, 'at': v6, 'by': v7}
        self.tbl_model_audit = QTableWidget(0, 3)
        self.tbl_model_audit.setHorizontalHeaderLabels(['Sự kiện','Chi tiết','Thời gian'])
        try:
            hdr = self.tbl_model_audit.horizontalHeader(); hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        try:
            self.tbl_model_audit.setMinimumHeight(180)
            self.tbl_model_audit.verticalHeader().setDefaultSectionSize(34)
        except Exception:
            pass
        mv.addWidget(self.tbl_model_audit)
        self.tbl_model_activity = QTableWidget(0, 13)
        self.tbl_model_activity.setHorizontalHeaderLabels(['Mô hình','Trạng thái','Ngưỡng','AUC','Độ chính xác','F1','Hôm nay','Tuần','Tháng','Huấn luyện lúc','Huấn luyện bởi','Tập tin','Trạng thái'])
        try:
            hdr2 = self.tbl_model_activity.horizontalHeader(); hdr2.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        try:
            self.tbl_model_activity.setMinimumHeight(240)
            self.tbl_model_activity.verticalHeader().setDefaultSectionSize(34)
        except Exception:
            pass
        mv.addWidget(self.tbl_model_activity)
        if hasattr(self.user, 'is_admin') and self.user.is_admin():
            layout.insertWidget(1, model_card)
        if hasattr(self.user, 'is_admin') and self.user.is_admin():
            health_card = QFrame(); health_card.setObjectName('Card')
            hv = QVBoxLayout(health_card); hv.setContentsMargins(16,16,16,16); hv.setSpacing(12)
            ht = QLabel('Sức khỏe mô hình / kiểm tra độ lệch'); ht.setObjectName('SectionTitle'); hv.addWidget(ht)
            def make_row():
                r = QHBoxLayout(); r.setSpacing(8)
                d = QLabel(''); d.setObjectName('HealthDesc')
                c = QLabel(''); c.setObjectName('ChipStable')
                r.addWidget(d); r.addSpacing(10); r.addWidget(c); r.addStretch()
                return r, d, c
            r1, d1, c1 = make_row(); hv.addLayout(r1)
            r2, d2, c2 = make_row(); hv.addLayout(r2)
            r3, d3, c3 = make_row(); hv.addLayout(r3)
            r4, d4, c4 = make_row(); hv.addLayout(r4)
            hv.addStretch(1)
            self.health_labels = {
                'data': {'desc': d1, 'chip': c1},
                'pred': {'desc': d2, 'chip': c2},
                'feat': {'desc': d3, 'chip': c3},
                'acc': {'desc': d4, 'chip': c4},
            }
            layout.insertWidget(2, health_card)
        scroll.setWidget(content)
        root.addWidget(scroll)
        try:
            self._apply_table_row_heights()
        except Exception:
            pass

    def refresh_report(self):
        try:
            db = get_db_connector()
            qs = get_query_service(db)
            if hasattr(self.user, 'is_admin') and self.user.is_admin():
                try:
                    self._update_model_activity(db)
                except Exception:
                    pass
                try:
                    self._update_health_card(db)
                except Exception:
                    pass
                db.close()
                return
            # KPI
            tr = self.cmb_time.currentText()
            sf = self.cmb_status.currentText()
            uid = self.user.id if self.view_mode == 'own_data_only' else None
            start_iso = self.date_start.date().toString('yyyy-MM-dd') if hasattr(self, 'date_start') else None
            end_iso = self.date_end.date().toString('yyyy-MM-dd') if hasattr(self, 'date_end') else None
            s = qs.get_prediction_stats_range(start_iso, end_iso, sf, uid)
            if s.get('total_predictions', 0) == 0:
                s = qs.get_prediction_stats_filtered(tr, sf, uid)
            if s.get('total_predictions', 0) == 0:
                s = qs.get_prediction_stats()
            self.lbl_total.setText(f"Tổng dự báo: {s.get('total_predictions',0)}")
            self.lbl_high.setText(f"Nguy cơ cao: {s.get('high_risk_count',0)}")
            self.lbl_avg.setText(f"Xác suất TB: {s.get('avg_probability',0.0):.2f}")
            if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
                monthly = qs.get_monthly_default_rate_recent(months=12)
                self.tbl_monthly.setRowCount(len(monthly))
                for i, row in enumerate(monthly):
                    self.tbl_monthly.setItem(i, 0, QTableWidgetItem(row['period']))
                    self.tbl_monthly.setItem(i, 1, QTableWidgetItem(f"{row['rate']*100:.1f}%"))
                if self.tbl_monthly.rowCount() == 0:
                    self.tbl_monthly.setRowCount(1)
                    self.tbl_monthly.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_monthly.setItem(0, 1, QTableWidgetItem('-'))
                quarterly = qs.get_quarterly_high_risk_rate_recent(quarters=8)
                self.tbl_quarterly.setRowCount(len(quarterly))
                for i, row in enumerate(quarterly):
                    self.tbl_quarterly.setItem(i, 0, QTableWidgetItem(row['period']))
                    self.tbl_quarterly.setItem(i, 1, QTableWidgetItem(f"{row['rate']*100:.1f}%"))
                if self.tbl_quarterly.rowCount() == 0:
                    self.tbl_quarterly.setRowCount(1)
                    self.tbl_quarterly.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_quarterly.setItem(0, 1, QTableWidgetItem('-'))
            if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
                g, m, e = qs.get_demographics_counts_filtered(tr, uid)
                if not g and not m and not e:
                    g, m, e = qs.get_demographics_counts()
                def fill_map(tbl, mp):
                    items = list(mp.items())
                    tbl.setRowCount(len(items))
                    for i, (k, v) in enumerate(items):
                        tbl.setItem(i, 0, QTableWidgetItem(str(k)))
                        tbl.setItem(i, 1, QTableWidgetItem(str(v)))
                fill_map(self.tbl_gender, g); fill_map(self.tbl_marriage, m); fill_map(self.tbl_edu, e)
                if self.tbl_gender.rowCount() == 0:
                    self.tbl_gender.setRowCount(1)
                    self.tbl_gender.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_gender.setItem(0, 1, QTableWidgetItem('-'))
                if self.tbl_marriage.rowCount() == 0:
                    self.tbl_marriage.setRowCount(1)
                    self.tbl_marriage.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_marriage.setItem(0, 1, QTableWidgetItem('-'))
                if self.tbl_edu.rowCount() == 0:
                    self.tbl_edu.setRowCount(1)
                    self.tbl_edu.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_edu.setItem(0, 1, QTableWidgetItem('-'))
            if not (hasattr(self.user, 'is_admin') and self.user.is_admin()):
                top = qs.get_top_predictions_join_customers_filtered(ascending=False, time_range=tr, limit=10, user_id=uid)
                if not top:
                    top = qs.get_top_predictions_join_customers(limit=10, ascending=False)
                self.tbl_top.setRowCount(len(top))
                for i, r in enumerate(top):
                    self.tbl_top.setItem(i, 0, QTableWidgetItem(str(r.get('customer_name') or '-')))
                    self.tbl_top.setItem(i, 1, QTableWidgetItem(str(r.get('customer_id_card') or '-')))
                    self.tbl_top.setItem(i, 2, QTableWidgetItem(f"{r.get('probability',0.0):.2f}"))
                    self.tbl_top.setItem(i, 3, QTableWidgetItem('Cao' if r.get('label')==1 else 'Thấp'))
                bottom = qs.get_top_predictions_join_customers_filtered(ascending=True, time_range=tr, limit=10, user_id=uid)
                if not bottom:
                    bottom = qs.get_top_predictions_join_customers(limit=10, ascending=True)
                self.tbl_bottom.setRowCount(len(bottom))
                for i, r in enumerate(bottom):
                    self.tbl_bottom.setItem(i, 0, QTableWidgetItem(str(r.get('customer_name') or '-')))
                    self.tbl_bottom.setItem(i, 1, QTableWidgetItem(str(r.get('customer_id_card') or '-')))
                    self.tbl_bottom.setItem(i, 2, QTableWidgetItem(f"{r.get('probability',0.0):.2f}"))
                    self.tbl_bottom.setItem(i, 3, QTableWidgetItem('Cao' if r.get('label')==1 else 'Thấp'))
                if self.tbl_top.rowCount() == 0:
                    self.tbl_top.setRowCount(1)
                    self.tbl_top.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_top.setItem(0, 1, QTableWidgetItem('-'))
                    self.tbl_top.setItem(0, 2, QTableWidgetItem('-'))
                    self.tbl_top.setItem(0, 3, QTableWidgetItem('-'))
                if self.tbl_bottom.rowCount() == 0:
                    self.tbl_bottom.setRowCount(1)
                    self.tbl_bottom.setItem(0, 0, QTableWidgetItem('Không có dữ liệu'))
                    self.tbl_bottom.setItem(0, 1, QTableWidgetItem('-'))
                    self.tbl_bottom.setItem(0, 2, QTableWidgetItem('-'))
                    self.tbl_bottom.setItem(0, 3, QTableWidgetItem('-'))
            # Latest detail by range or time filter
            latest = qs.get_predictions_join_customers_range(start_iso, end_iso, sf, limit=50, user_id=uid)
            if not latest:
                latest = qs.get_predictions_join_customers(time_range=tr, status_filter=sf, limit=50, user_id=uid)
            if not latest:
                latest = qs.get_latest_day_predictions_join_customers(limit=50)
            self.tbl_latest.setRowCount(len(latest))
            for i, r in enumerate(latest):
                self.tbl_latest.setItem(i, 0, QTableWidgetItem(str(r.get('customer_name') or '-')))
                self.tbl_latest.setItem(i, 1, QTableWidgetItem(str(r.get('customer_id_card') or '-')))
                self.tbl_latest.setItem(i, 2, QTableWidgetItem(f"{r.get('probability',0.0):.2f}"))
                self.tbl_latest.setItem(i, 3, QTableWidgetItem('Cao' if r.get('label')==1 else 'Thấp'))
                self.tbl_latest.setItem(i, 4, QTableWidgetItem(str(r.get('LIMIT_BAL') or '-')))
                self.tbl_latest.setItem(i, 5, QTableWidgetItem(str(r.get('AGE') or '-')))
                self.tbl_latest.setItem(i, 6, QTableWidgetItem(str(r.get('PAY_0') or '-')))
                self.tbl_latest.setItem(i, 7, QTableWidgetItem(str(r.get('BILL_AMT1') or '-')))
            if self.tbl_latest.rowCount() == 0:
                self.tbl_latest.setRowCount(1)
                for c in range(8):
                    self.tbl_latest.setItem(0, c, QTableWidgetItem('-'))
            self.info.setText(f"Chế độ: {'dữ liệu của tôi' if self.view_mode=='own_data_only' else 'tất cả'} · Bộ lọc: {tr}, {sf} · Bản ghi: {self.tbl_latest.rowCount()}")
            pass
            db.close()
        except Exception:
            try:
                db.close()
            except Exception:
                pass

    def export_csv(self):
        try:
            from pathlib import Path
            out_dir = Path(__file__).resolve().parents[1] / 'outputs' / 'reports'
            out_dir.mkdir(parents=True, exist_ok=True)
            fp = out_dir / 'latest_day_predictions.csv'
            import csv
            with open(fp, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['Khách','CMND','Xác suất','Nhãn','Hạn mức','Tuổi','PAY_0','BILL_AMT1'])
                for i in range(self.tbl_latest.rowCount()):
                    row = [self.tbl_latest.item(i, c).text() if self.tbl_latest.item(i, c) else '' for c in range(8)]
                    w.writerow(row)
            QMessageBox.information(self, 'Xuất CSV', f'Đã lưu: {fp}')
        except Exception:
            pass

    def export_html(self):
        try:
            from pathlib import Path
            out_dir = Path(__file__).resolve().parents[1] / 'outputs' / 'reports'
            out_dir.mkdir(parents=True, exist_ok=True)
            fp = out_dir / 'report_snapshot.html'
            html = ['<html><head><meta charset="utf-8"><title>Ảnh chụp báo cáo</title></head><body>']
            if hasattr(self.user, 'is_admin') and self.user.is_admin():
                html.append('<h2>Hoạt động mô hình ML</h2>')
                html.append('<table border="1" cellspacing="0" cellpadding="6">')
                html.append('<thead><tr>')
                for c in range(self.tbl_model_activity.columnCount()):
                    item = self.tbl_model_activity.horizontalHeaderItem(c)
                    html.append(f'<th>{item.text() if item else ""}</th>')
                html.append('</tr></thead><tbody>')
                for i in range(self.tbl_model_activity.rowCount()):
                    html.append('<tr>')
                    for c in range(self.tbl_model_activity.columnCount()):
                        item = self.tbl_model_activity.item(i, c)
                        html.append(f'<td>{item.text() if item else ""}</td>')
                    html.append('</tr>')
                html.append('</tbody></table>')
                if hasattr(self, 'health_labels') and self.health_labels:
                    html.append('<h2>Sức khỏe mô hình / độ lệch</h2>')
                    html.append('<ul>')
                    html.append(f'<li>{self.health_labels["data"]["desc"].text()} ({self.health_labels["data"]["chip"].text()})</li>')
                    html.append(f'<li>{self.health_labels["pred"]["desc"].text()} ({self.health_labels["pred"]["chip"].text()})</li>')
                    html.append(f'<li>{self.health_labels["feat"]["desc"].text()} ({self.health_labels["feat"]["chip"].text()})</li>')
                    html.append(f'<li>{self.health_labels["acc"]["desc"].text()} ({self.health_labels["acc"]["chip"].text()})</li>')
                    html.append('</ul>')
            else:
                html.append(f'<h2>Tổng dự báo: {self.lbl_total.text().split(": ")[-1]}</h2>')
                html.append(f'<h2>Nguy cơ cao: {self.lbl_high.text().split(": ")[-1]}</h2>')
                html.append(f'<h2>Xác suất TB: {self.lbl_avg.text().split(": ")[-1]}</h2>')
                html.append('<h3>Tháng gần đây</h3><ul>')
                for i in range(self.tbl_monthly.rowCount()):
                    period = self.tbl_monthly.item(i,0).text(); rate = self.tbl_monthly.item(i,1).text()
                    html.append(f'<li>{period}: {rate}</li>')
                html.append('</ul><h3>Quý gần đây</h3><ul>')
                for i in range(self.tbl_quarterly.rowCount()):
                    period = self.tbl_quarterly.item(i,0).text(); rate = self.tbl_quarterly.item(i,1).text()
                    html.append(f'<li>{period}: {rate}</li>')
                html.append('</ul>')
            html.append('</body></html>')
            fp.write_text('\n'.join(html), encoding='utf-8')
            QMessageBox.information(self, 'Xuất HTML', f'Đã lưu: {fp}')
        except Exception:
            pass

    def _update_model_activity(self, db):
        name = None; thr = None; auc = None; acc = None; f1 = None; at = None; by = None
        try:
            if _HaveModelMgmt:
                svc = ModelManagementService(db)
                active = svc.get_active_model()
                name = active.get('model_name') if active else None
            else:
                row = db.fetch_one("SELECT model_name FROM model_registry WHERE is_active = 1 LIMIT 1")
                name = row[0] if row and row[0] else None
        except Exception:
            name = None
        try:
            if name:
                row = db.fetch_one("SELECT auc_score, accuracy, f1_score, trained_at, trained_by, threshold FROM model_registry WHERE model_name = %s", (name,))
                if row:
                    auc = float(row[0]) if row[0] is not None else None
                    acc = float(row[1]) if row[1] is not None else None
                    f1 = float(row[2]) if row[2] is not None else None
                    at = str(row[3]) if row[3] is not None else None
                    by = str(row[4]) if row[4] is not None else None
                    try:
                        tdb = float(row[5]) if row[5] is not None else None
                        if tdb is not None:
                            thr = tdb
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            if name and thr is None:
                import numpy as np
                eval_path = Path(__file__).resolve().parents[1] / 'outputs' / 'evaluation' / 'evaluation_data.npz'
                if eval_path.exists():
                    data = np.load(eval_path, allow_pickle=True)
                    best = data.get('best_thresholds', None)
                    if best is not None:
                        d = best.item() if hasattr(best, 'item') else best
                        val = d.get(name, None)
                        thr = float(val) if val is not None else None
        except Exception:
            thr = None
        try:
            rows = []
            try:
                import numpy as np
                eval_path = Path(__file__).resolve().parents[1] / 'outputs' / 'evaluation' / 'evaluation_data.npz'
                if eval_path.exists():
                    data = np.load(eval_path, allow_pickle=True)
                    audit = data.get('threshold_audit', None)
                    if audit is not None:
                        arr = audit if not hasattr(audit, 'tolist') else audit.tolist()
                        if isinstance(arr, np.ndarray):
                            arr = arr.tolist()
                        if isinstance(arr, list):
                            last = arr[-5:] if len(arr) > 5 else arr
                            for item in last:
                                try:
                                    ev = 'Threshold update'
                                    det = f"{item.get('model','')} → {float(item.get('value',0.0)):.2f} by {item.get('user','')}"
                                    ts = str(item.get('ts',''))
                                    rows.append((ev, det, ts))
                                except Exception:
                                    pass
            except Exception:
                pass
            try:
                q = "SELECT model_name, trained_by, trained_at, is_active FROM model_registry ORDER BY trained_at DESC LIMIT 5"
                r = db.fetch_all(q)
                for row in r:
                    ev = 'Kho mô hình'
                    det = f"{row[0]} by {row[1]} {'(active)' if bool(row[3]) else ''}"
                    ts = str(row[2]) if row[2] is not None else ''
                    rows.append((ev, det, ts))
            except Exception:
                pass
            self.tbl_model_audit.setRowCount(len(rows))
            for i, (ev, det, ts) in enumerate(rows):
                self.tbl_model_audit.setItem(i, 0, QTableWidgetItem(ev))
                self.tbl_model_audit.setItem(i, 1, QTableWidgetItem(det))
                self.tbl_model_audit.setItem(i, 2, QTableWidgetItem(ts))
        except Exception:
            try:
                self.tbl_model_audit.setRowCount(1)
                self.tbl_model_audit.setItem(0,0,QTableWidgetItem('—'))
                self.tbl_model_audit.setItem(0,1,QTableWidgetItem('—'))
                self.tbl_model_audit.setItem(0,2,QTableWidgetItem('—'))
            except Exception:
                pass
        try:
            models = ['XGBoost','LightGBM','CatBoost','RandomForest','Logistic','NeuralNet','Voting','Stacking']
            name_map = {'Logistic':'LogisticRegression','NeuralNet':'Neural Network'}
            eval_thr = {}
            try:
                import numpy as np
                eval_path = Path(__file__).resolve().parents[1] / 'outputs' / 'evaluation' / 'evaluation_data.npz'
                if eval_path.exists():
                    data = np.load(eval_path, allow_pickle=True)
                    best = data.get('best_thresholds', None)
                    if best is not None:
                        d = best.item() if hasattr(best, 'item') else best
                        if isinstance(d, dict):
                            eval_thr = {str(k): float(v) for k, v in d.items() if v is not None}
            except Exception:
                eval_thr = {}
            rows = []
            for m in models:
                mn = name_map.get(m, m)
                is_active = ''
                auc_v = None; acc_v = None; f1_v = None; at_v = None; by_v = None; file_v = ''; tdb_v = None
                try:
                    row = db.fetch_one("SELECT is_active, auc_score, accuracy, f1_score, trained_at, trained_by, threshold, model_path FROM model_registry WHERE model_name = %s", (mn,))
                    if row:
                        is_active = '✓' if bool(row[0]) else ''
                        auc_v = float(row[1]) if row[1] is not None else None
                        acc_v = float(row[2]) if row[2] is not None else None
                        f1_v = float(row[3]) if row[3] is not None else None
                        at_v = str(row[4]) if row[4] is not None else ''
                        by_v = str(row[5]) if row[5] is not None else ''
                        tdb_v = float(row[6]) if row[6] is not None else None
                        mp = row[7]
                        try:
                            from pathlib import Path
                            file_v = '✓' if (mp and Path(mp).exists()) else ''
                        except Exception:
                            file_v = ''
                except Exception:
                    pass
                thr_v = tdb_v if tdb_v is not None else eval_thr.get(mn, None)
                try:
                    row = db.fetch_one("SELECT COUNT(*) FROM predictions_log WHERE model_name = %s AND DATE(created_at) = CURDATE()", (mn,))
                    day_v = int(row[0]) if row and row[0] is not None else 0
                except Exception:
                    day_v = 0
                try:
                    row = db.fetch_one("SELECT COUNT(*) FROM predictions_log WHERE model_name = %s AND created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)", (mn,))
                    week_v = int(row[0]) if row and row[0] is not None else 0
                except Exception:
                    week_v = 0
                try:
                    row = db.fetch_one("SELECT COUNT(*) FROM predictions_log WHERE model_name = %s AND DATE_FORMAT(created_at,'%Y-%m') = DATE_FORMAT(CURDATE(),'%Y-%m')", (mn,))
                    month_v = int(row[0]) if row and row[0] is not None else 0
                except Exception:
                    month_v = 0
                status_parts = []
                if not file_v:
                    status_parts.append('Thiếu file')
                if acc_v is None and auc_v is None and f1_v is None:
                    status_parts.append('Chưa train')
                if thr_v is None:
                    status_parts.append('Thiếu threshold')
                if day_v == 0 and week_v == 0 and month_v == 0:
                    status_parts.append('Không có hoạt động')
                if is_active != '✓':
                    status_parts.append('Không hoạt động')
                status_text = ', '.join(status_parts) if status_parts else 'Ổn định'
                rows.append([
                    m,
                    is_active,
                    f"{thr_v:.2f}" if isinstance(thr_v, float) else '—',
                    f"{auc_v:.3f}" if isinstance(auc_v, float) else '—',
                    f"{acc_v:.3f}" if isinstance(acc_v, float) else '—',
                    f"{f1_v:.3f}" if isinstance(f1_v, float) else '—',
                    str(day_v),
                    str(week_v),
                    str(month_v),
                    at_v or '—',
                    by_v or '—',
                    file_v or '—',
                    status_text
                ])
            self.tbl_model_activity.setRowCount(len(rows))
            for i, cols in enumerate(rows):
                for j, val in enumerate(cols):
                    self.tbl_model_activity.setItem(i, j, QTableWidgetItem(val))
        except Exception:
            try:
                self.tbl_model_activity.setRowCount(1)
                for j in range(13):
                    self.tbl_model_activity.setItem(0, j, QTableWidgetItem('—'))
            except Exception:
                pass
        self._model_labels['name'].setText(str(name or '—'))
        self._model_labels['thr'].setText(f"{thr:.2f}" if isinstance(thr, float) else '—')
        self._model_labels['auc'].setText(f"{auc:.3f}" if isinstance(auc, float) else '—')
        self._model_labels['acc'].setText(f"{acc:.3f}" if isinstance(acc, float) else '—')
        self._model_labels['f1'].setText(f"{f1:.3f}" if isinstance(f1, float) else '—')
        self._model_labels['at'].setText(str(at or '—'))
        self._model_labels['by'].setText(str(by or '—'))

    def _apply_table_row_heights(self):
        try:
            for tbl in [getattr(self, 'tbl_monthly', None), getattr(self, 'tbl_quarterly', None), self.tbl_gender, self.tbl_marriage, self.tbl_edu, self.tbl_top, self.tbl_bottom, self.tbl_latest, self.tbl_model_audit, self.tbl_model_activity]:
                try:
                    if tbl:
                        vh = tbl.verticalHeader()
                        vh.setDefaultSectionSize(30)
                except Exception:
                    pass
        except Exception:
            pass

    def _update_health_card(self, db):
        if not hasattr(self, 'health_labels') or not self.health_labels:
            return
        try:
            # Default rate drift (monthly series)
            try:
                from services.integration import get_query_service
            except Exception:
                from integration import get_query_service
            qs = get_query_service(db)
            monthly = qs.get_monthly_default_rate_recent(months=12)
            delta = 0.0
            if monthly and len(monthly) >= 2:
                delta = (monthly[-1]['rate'] - monthly[-2]['rate']) * 100
            status = 'Cảnh báo' if abs(delta) >= 5.0 else 'Ổn định'
            self.health_labels['data']['desc'].setText(f"Độ lệch tỷ lệ vỡ nợ: {delta:+.1f}%")
            self.health_labels['data']['chip'].setText(status)
            self.health_labels['data']['chip'].setObjectName('ChipWarning' if status=='Cảnh báo' else 'ChipStable')
            try:
                self.health_labels['data']['chip'].setStyleSheet("")
            except Exception:
                pass
            # Prediction drift (avg probability vs previous month rate)
            cur = qs.get_prediction_stats() if hasattr(qs, 'get_prediction_stats') else {}
            avg_prob = float(cur.get('avg_probability', 0.0))
            prev_rate = monthly[-2]['rate'] if monthly and len(monthly) >= 2 else avg_prob
            pred_delta = (avg_prob - prev_rate) * 100
            pstatus = 'Cảnh báo' if abs(pred_delta) >= 5.0 else 'Ổn định'
            self.health_labels['pred']['desc'].setText(f"Độ lệch dự báo: {pred_delta:+.1f}%")
            self.health_labels['pred']['chip'].setText(pstatus)
            self.health_labels['pred']['chip'].setObjectName('ChipWarning' if pstatus=='Cảnh báo' else 'ChipStable')
            try:
                self.health_labels['pred']['chip'].setStyleSheet("")
            except Exception:
                pass
            # Feature drift proxy (quarterly high-risk rate changes)
            quarterly = qs.get_quarterly_high_risk_rate_recent(quarters=8)
            feat_delta = 0.0
            if quarterly and len(quarterly) >= 2:
                feat_delta = (quarterly[-1]['rate'] - quarterly[-2]['rate']) * 100
            fstatus = 'Cảnh báo' if abs(feat_delta) >= 10.0 else 'Ổn định'
            self.health_labels['feat']['desc'].setText(f"Độ lệch PAY_0: {feat_delta:+.1f}%")
            self.health_labels['feat']['chip'].setText(fstatus)
            self.health_labels['feat']['chip'].setObjectName('ChipWarning' if fstatus=='Cảnh báo' else 'ChipStable')
            try:
                self.health_labels['feat']['chip'].setStyleSheet("")
            except Exception:
                pass
            # Model accuracy (from evaluation data)
            acc_pct = None
            try:
                if load_evaluation_data:
                    eval_data = load_evaluation_data()
                    y_test = eval_data.get('y_test') if isinstance(eval_data, dict) else None
                    preds_dict = eval_data.get('predictions', {}) if isinstance(eval_data, dict) else {}
                    preds = preds_dict.get('XGBoost', None)
                    if preds is None and preds_dict:
                        k = next(iter(preds_dict))
                        preds = preds_dict.get(k)
                    import numpy as np
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
            pass
