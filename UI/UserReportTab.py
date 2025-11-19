from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea
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

class UserReportTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.view_mode = 'own_data_only' if self.user.is_user() else 'all'
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
        self.btn_export = QPushButton('Export Excel')
        filters.addStretch()
        filters.addWidget(self.btn_export)
        layout.addLayout(filters)
        stats = QHBoxLayout()
        stats.addWidget(QLabel('Tổng dự báo: 15'))
        stats.addWidget(QLabel('Nguy cơ cao: 8'))
        stats.addWidget(QLabel('Nguy cơ thấp: 7'))
        stats.addWidget(QLabel('Trung bình: 62%'))
        layout.addLayout(stats)
        self.table = QTableWidget(5, 6)
        self.table.setHorizontalHeaderLabels(['STT', 'Khách hàng', 'Ngày', 'Kết quả', 'Xác suất', 'Thao tác'])
        self.load_recent()
        layout.addWidget(self.table)
        self.info = QLabel()
        self.info.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.info.setText('Chế độ: dữ liệu của tôi' if self.view_mode == 'own_data_only' else 'Chế độ: tất cả')
        layout.addWidget(self.info)
        scroll.setWidget(content)
        root.addWidget(scroll)

    def load_recent(self):
        try:
            db = get_db_connector()
            qs = get_query_service(db)
            uid = self.user.id if self.view_mode == 'own_data_only' else None
            rows = qs.get_predictions_join_customers('Hôm nay', 'Tất cả', limit=20, user_id=uid)
            if not rows:
                rows = qs.get_recent_predictions_join_customers('today', limit=20)
                if uid is not None:
                    rows = [r for r in rows if int(r.get('user_id') or 0) == uid]
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                self.table.setItem(i, 1, QTableWidgetItem(str(r.get('customer_name') or r.get('customer_id') or '-')))
                self.table.setItem(i, 2, QTableWidgetItem(str(r.get('created_at'))))
                self.table.setItem(i, 3, QTableWidgetItem('Nguy cơ cao' if int(r.get('predicted_label') or r.get('label') or 0)==1 else 'Nguy cơ thấp'))
                self.table.setItem(i, 4, QTableWidgetItem(f"{float(r.get('probability') or 0.0):.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem('Xem'))
            if self.table.rowCount() == 0:
                self.table.setRowCount(1)
                for c in range(6):
                    self.table.setItem(0, c, QTableWidgetItem('-'))
            db.close()
        except Exception:
            try:
                db.close()
            except Exception:
                pass
