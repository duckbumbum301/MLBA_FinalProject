from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QHeaderView, QFileDialog
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

class ReportTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.view_mode = 'all'
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(16,16,16,16); layout.setSpacing(16)
        filters = QHBoxLayout()
        self.cmb_time = QComboBox()
        self.cmb_time.addItems(['Hôm nay', 'Tuần này', 'Tháng này'])
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(['Tất cả', 'Nguy cơ cao', 'Nguy cơ thấp'])
        filters.addWidget(QLabel('Thời gian:'))
        filters.addWidget(self.cmb_time)
        filters.addWidget(QLabel('Trạng thái:'))
        filters.addWidget(self.cmb_status)
        self.btn_export = QPushButton('Export CSV')
        filters.addStretch()
        filters.addWidget(self.btn_export)
        layout.addLayout(filters)
        try:
            self.output_dir = base_dir / 'output'
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.output_dir = base_dir
        stats = QHBoxLayout()
        self.stat_total = QLabel('Tổng dự báo: 0')
        self.stat_high = QLabel('Nguy cơ cao: 0')
        self.stat_low  = QLabel('Nguy cơ thấp: 0')
        self.stat_avg  = QLabel('Trung bình: 0%')
        stats.addWidget(self.stat_total)
        stats.addWidget(self.stat_high)
        stats.addWidget(self.stat_low)
        stats.addWidget(self.stat_avg)
        layout.addLayout(stats)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['STT', 'Khách hàng', 'Ngày', 'Kết quả', 'Xác suất', 'Thao tác'])
        try:
            hdr = self.table.horizontalHeader()
            hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        self._connect_events()
        self.load_data()
        layout.addWidget(self.table)
        self.info = QLabel()
        self.info.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.info.setText('Chế độ: dữ liệu của tôi' if self.view_mode == 'own_data_only' else 'Chế độ: tất cả')
        layout.addWidget(self.info)
        scroll.setWidget(content)
        root.addWidget(scroll)

    def _connect_events(self):
        try:
            self.cmb_time.currentTextChanged.connect(self.load_data)
            self.cmb_status.currentTextChanged.connect(self.load_data)
            self.btn_export.clicked.connect(self._export_csv)
        except Exception:
            pass

    def load_data(self):
        try:
            db = get_db_connector()
            qs = get_query_service(db)
            period = self.cmb_time.currentText()
            rows = []
            if hasattr(qs, 'get_recent_predictions_join_customers'):
                rows = qs.get_recent_predictions_join_customers(period=period, limit=200)
            else:
                rows = qs.get_recent_predictions(limit=200)
            filtered = []
            status = self.cmb_status.currentText()
            for r in rows:
                include = True
                if status == 'Nguy cơ cao':
                    include = float(r.get('probability',0.0)) >= 0.60
                elif status == 'Nguy cơ thấp':
                    include = float(r.get('probability',0.0)) < 0.60
                if self.view_mode == 'own_data_only':
                    try:
                        uid_col = r.get('user_id')
                        if uid_col is not None:
                            include = include and (int(uid_col) == int(self.user.id))
                        else:
                            raw = r.get('raw_input_json')
                            if raw:
                                obj = json.loads(raw)
                                uid = obj.get('user_id')
                                include = include and (uid == self.user.id)
                    except Exception:
                        include = include
                if include:
                    filtered.append(r)
            # Update stats
            total = len(filtered)
            high = sum(1 for r in filtered if float(r.get('probability',0.0)) >= 0.60)
            low  = total - high
            avg  = (sum(float(r.get('probability',0.0)) for r in filtered)/total if total>0 else 0.0)*100
            self.stat_total.setText(f'Tổng dự báo: {total}')
            self.stat_high.setText(f'Nguy cơ cao: {high}')
            self.stat_low.setText(f'Nguy cơ thấp: {low}')
            self.stat_avg.setText(f'Trung bình: {avg:.0f}%')
            # Fill table
            self.table.setRowCount(total)
            for i, r in enumerate(filtered):
                self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                cust_id = str(r.get('customer_id') or '-')
                self.table.setItem(i, 1, QTableWidgetItem(cust_id))
                try:
                    dt = r.get('created_at')
                    if hasattr(dt, 'strftime'):
                        date_str = dt.strftime('%Y-%m-%d')
                    else:
                        s = str(dt)
                        date_str = s[:10]
                except Exception:
                    date_str = str(r.get('created_at'))
                self.table.setItem(i, 2, QTableWidgetItem(date_str))
                lbl = 'Nguy cơ cao' if float(r.get('probability',0.0)) >= 0.60 else 'Nguy cơ thấp'
                self.table.setItem(i, 3, QTableWidgetItem(lbl))
                self.table.setItem(i, 4, QTableWidgetItem(f"{float(r.get('probability',0.0)):.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem('View'))
            db.close()
        except Exception:
            pass

    def _export_csv(self):
        try:
            import csv
            from datetime import datetime
            default_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            initial = str((self.output_dir / default_name).resolve())
            fname, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo CSV", initial, "CSV Files (*.csv)")
            if not fname:
                return
            with open(fname, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                headers = ['STT','Khách hàng','Ngày','Kết quả','Xác suất','Thao tác']
                w.writerow(headers)
                for i in range(self.table.rowCount()):
                    row = [
                        self.table.item(i,0).text() if self.table.item(i,0) else '',
                        self.table.item(i,1).text() if self.table.item(i,1) else '',
                        ("'" + self.table.item(i,2).text()) if self.table.item(i,2) else '',
                        self.table.item(i,3).text() if self.table.item(i,3) else '',
                        self.table.item(i,4).text() if self.table.item(i,4) else '',
                        self.table.item(i,5).text() if self.table.item(i,5) else '',
                    ]
                    w.writerow(row)
            self.btn_export.setText('Exported')
        except Exception:
            self.btn_export.setText('Export lỗi')
