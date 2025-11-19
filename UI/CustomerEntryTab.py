from PyQt6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QScrollArea
from PyQt6.QtCore import Qt
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .integration import get_db_connector, get_query_service
except Exception:
    from integration import get_db_connector, get_query_service
try:
    from pathlib import Path as _P
    proj = _P(__file__).resolve().parents[1] / 'MLBA_FinalProject'
    sys.path.insert(0, str(proj))
    from models.customer import Customer
except Exception:
    Customer = None

class CustomerEntryTab(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        content = QWidget(); self.layout = QVBoxLayout(content); self.layout.setContentsMargins(16,16,16,16); self.layout.setSpacing(16)
        header = QHBoxLayout()
        self.searchBox = QLineEdit(); self.searchBox.setPlaceholderText('Tìm theo tên hoặc CMND/CCCD')
        btnSearch = QPushButton('Tìm'); btnSearch.clicked.connect(self.search_customers)
        btnImport = QPushButton('Import CSV (100)'); btnImport.clicked.connect(self.import_csv_sample)
        header.addWidget(self.searchBox)
        header.addWidget(btnSearch)
        header.addWidget(btnImport)
        header.addStretch()
        self.layout.addLayout(header)
        form = QFormLayout()
        self.txtName = QLineEdit()
        self.txtIDCard = QLineEdit()
        self.spnLimit = QDoubleSpinBox(); self.spnLimit.setRange(0, 10000000); self.spnLimit.setValue(50000)
        self.cmbSex = QComboBox(); self.cmbSex.addItems(['1','2'])
        self.cmbEdu = QComboBox(); self.cmbEdu.addItems(['1','2','3','4'])
        self.cmbMar = QComboBox(); self.cmbMar.addItems(['1','2','3'])
        self.spnAge = QDoubleSpinBox(); self.spnAge.setRange(18, 100); self.spnAge.setValue(30); self.spnAge.setDecimals(0)
        form.addRow('Tên khách hàng:', self.txtName)
        form.addRow('CMND/CCCD:', self.txtIDCard)
        form.addRow('LIMIT_BAL:', self.spnLimit)
        form.addRow('SEX:', self.cmbSex)
        form.addRow('EDUCATION:', self.cmbEdu)
        form.addRow('MARRIAGE:', self.cmbMar)
        form.addRow('AGE:', self.spnAge)
        self.layout.addLayout(form)
        actions = QHBoxLayout()
        self.btnSave = QPushButton('Lưu Khách Hàng')
        self.btnSave.clicked.connect(self.save_customer)
        actions.addWidget(self.btnSave)
        self.btnLoadSelected = QPushButton('Nạp từ danh sách')
        self.btnLoadSelected.clicked.connect(self.load_selected_row)
        actions.addWidget(self.btnLoadSelected)
        self.lblStatus = QLabel()
        actions.addWidget(self.lblStatus)
        actions.addStretch()
        self.layout.addLayout(actions)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['ID','Full Name','Citizen ID','Sex','Education','Marriage','Age'])
        self.layout.addWidget(self.table)
        scroll.setWidget(content)
        root.addWidget(scroll)

    def save_customer(self):
        if Customer is None:
            self.lblStatus.setText('Model Customer không khả dụng')
            return
        input_dict = {
            'LIMIT_BAL': float(self.spnLimit.value()),
            'SEX': int(self.cmbSex.currentText()),
            'EDUCATION': int(self.cmbEdu.currentText()),
            'MARRIAGE': int(self.cmbMar.currentText()),
            'AGE': int(self.spnAge.value()),
        }
        for key in ['PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6','PAY_7','PAY_8','PAY_9','PAY_10','PAY_11','PAY_12']:
            input_dict[key] = 0
        for i in range(1,13):
            input_dict[f'BILL_AMT{i}'] = 0.0
            input_dict[f'PAY_AMT{i}'] = 0.0
        customer = Customer(
            customer_name=self.txtName.text().strip() or None,
            customer_id_card=self.txtIDCard.text().strip() or None,
            **input_dict
        )
        try:
            db = get_db_connector()
            qs = get_query_service(db)
            cid = qs.save_customer(customer)
            self.lblStatus.setText(f'Đã lưu, ID={cid}')
            self.search_customers()
            db.close()
        except Exception:
            self.lblStatus.setText('Không thể lưu')

    def search_customers(self):
        kw = self.searchBox.text().strip()
        db = get_db_connector()
        qs = get_query_service(db)
        rows = qs.search_customers(kw, limit=100) if kw else qs.list_customers(limit=100)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(r['customer_name'] or '')))
            self.table.setItem(i, 2, QTableWidgetItem(str(r['customer_id_card'] or '')))
            self.table.setItem(i, 3, QTableWidgetItem(str(r['SEX'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(r['EDUCATION'])))
            self.table.setItem(i, 5, QTableWidgetItem(str(r['MARRIAGE'])))
            self.table.setItem(i, 6, QTableWidgetItem(str(r['AGE'])))
        db.close()

    def load_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            return
        try:
            cust_id = int(self.table.item(row, 0).text())
        except Exception:
            return
        db = get_db_connector()
        qs = get_query_service(db)
        c = qs.get_customer_by_id(cust_id)
        db.close()
        if not c:
            return
        self.txtName.setText(c.customer_name or '')
        self.txtIDCard.setText(c.customer_id_card or '')
        self.spnLimit.setValue(float(c.LIMIT_BAL or 0))
        self.cmbSex.setCurrentText(str(c.SEX))
        self.cmbEdu.setCurrentText(str(c.EDUCATION))
        self.cmbMar.setCurrentText(str(c.MARRIAGE))
        self.spnAge.setValue(float(c.AGE or 0))

    def import_csv_sample(self):
        from pathlib import Path
        import pandas as pd
        root = Path(__file__).resolve().parents[1]
        csv = root / 'MLBA_FinalProject' / 'UCI_Credit_Card_12months.csv'
        if not csv.exists():
            self.lblStatus.setText('Không thấy CSV 12 tháng')
            return
        try:
            df = pd.read_csv(csv)
            df = df.head(100)
            db = get_db_connector()
            qs = get_query_service(db)
            count = 0
            for _, r in df.iterrows():
                name = r.get('FULL NAME') if 'FULL NAME' in df.columns else None
                cid = r.get('CITIZEN ID') if 'CITIZEN ID' in df.columns else None
                customer = Customer(
                    customer_name=str(name) if name is not None else None,
                    customer_id_card=str(cid) if cid is not None else None,
                    LIMIT_BAL=float(r['LIMIT_BAL']) if 'LIMIT_BAL' in df.columns else 0.0,
                    SEX=int(r['SEX']), EDUCATION=int(r['EDUCATION']), MARRIAGE=int(r['MARRIAGE']), AGE=int(r['AGE']),
                    PAY_0=int(r['PAY_0']), PAY_2=int(r['PAY_2']), PAY_3=int(r['PAY_3']), PAY_4=int(r['PAY_4']), PAY_5=int(r['PAY_5']), PAY_6=int(r['PAY_6']),
                    PAY_7=int(r['PAY_7']) if 'PAY_7' in df.columns else 0,
                    PAY_8=int(r['PAY_8']) if 'PAY_8' in df.columns else 0,
                    PAY_9=int(r['PAY_9']) if 'PAY_9' in df.columns else 0,
                    PAY_10=int(r['PAY_10']) if 'PAY_10' in df.columns else 0,
                    PAY_11=int(r['PAY_11']) if 'PAY_11' in df.columns else 0,
                    PAY_12=int(r['PAY_12']) if 'PAY_12' in df.columns else 0,
                    BILL_AMT1=float(r['BILL_AMT1']), BILL_AMT2=float(r['BILL_AMT2']), BILL_AMT3=float(r['BILL_AMT3']), BILL_AMT4=float(r['BILL_AMT4']), BILL_AMT5=float(r['BILL_AMT5']), BILL_AMT6=float(r['BILL_AMT6']),
                    BILL_AMT7=float(r['BILL_AMT7']) if 'BILL_AMT7' in df.columns else 0,
                    BILL_AMT8=float(r['BILL_AMT8']) if 'BILL_AMT8' in df.columns else 0,
                    BILL_AMT9=float(r['BILL_AMT9']) if 'BILL_AMT9' in df.columns else 0,
                    BILL_AMT10=float(r['BILL_AMT10']) if 'BILL_AMT10' in df.columns else 0,
                    BILL_AMT11=float(r['BILL_AMT11']) if 'BILL_AMT11' in df.columns else 0,
                    BILL_AMT12=float(r['BILL_AMT12']) if 'BILL_AMT12' in df.columns else 0,
                    PAY_AMT1=float(r['PAY_AMT1']), PAY_AMT2=float(r['PAY_AMT2']), PAY_AMT3=float(r['PAY_AMT3']), PAY_AMT4=float(r['PAY_AMT4']), PAY_AMT5=float(r['PAY_AMT5']), PAY_AMT6=float(r['PAY_AMT6']),
                    PAY_AMT7=float(r['PAY_AMT7']) if 'PAY_AMT7' in df.columns else 0,
                    PAY_AMT8=float(r['PAY_AMT8']) if 'PAY_AMT8' in df.columns else 0,
                    PAY_AMT9=float(r['PAY_AMT9']) if 'PAY_AMT9' in df.columns else 0,
                    PAY_AMT10=float(r['PAY_AMT10']) if 'PAY_AMT10' in df.columns else 0,
                    PAY_AMT11=float(r['PAY_AMT11']) if 'PAY_AMT11' in df.columns else 0,
                    PAY_AMT12=float(r['PAY_AMT12']) if 'PAY_AMT12' in df.columns else 0,
                )
                if qs.save_customer(customer):
                    count += 1
            db.close()
            self.lblStatus.setText(f'Đã import {count} khách hàng')
            self.search_customers()
        except Exception:
            self.lblStatus.setText('Import lỗi')
