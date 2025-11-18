"""
PredictionTabWidget
Tab Dự Báo Rủi Ro với 41 trường input (12 tháng lịch sử) và hiển thị kết quả
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QCheckBox, QMessageBox, QScrollArea, QRadioButton, QButtonGroup,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import random

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.customer import Customer
from models.user import User
from services.ml_service import MLService
from services.query_service import QueryService


class PredictionTabWidget(QWidget):
    """
    Widget cho Tab Dự Báo Rủi Ro
    Chứa 41 trường input (12 tháng lịch sử) và hiển thị kết quả dự báo
    """
    
    EXCHANGE_RATE = 800  # 1 NT$ = 800 VND
    
    def __init__(self, user: User, query_service: QueryService):
        super().__init__()
        self.user = user
        self.query_service = query_service
        self.current_currency = 'VND'  # Mặc định VND
        
        # Init ML Service
        try:
            self.ml_service = MLService(model_name='XGBoost')
        except Exception as e:
            print(f"⚠ Không thể load ML model: {e}")
            self.ml_service = None
        
        # Init UI
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        main_layout = QVBoxLayout()
        
        # === CURRENCY SELECTOR ===
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("💰 Đơn vị tiền tệ:"))
        
        self.rbtn_vnd = QRadioButton("VND (Việt Nam Đồng)")
        self.rbtn_ntd = QRadioButton("NT$ (Đài Tệ)")
        self.rbtn_vnd.setChecked(True)  # Mặc định VND
        
        self.currency_group = QButtonGroup()
        self.currency_group.addButton(self.rbtn_vnd)
        self.currency_group.addButton(self.rbtn_ntd)
        self.currency_group.buttonClicked.connect(self.on_currency_changed)
        
        currency_layout.addWidget(self.rbtn_vnd)
        currency_layout.addWidget(self.rbtn_ntd)
        currency_layout.addStretch()
        
        main_layout.addLayout(currency_layout)
        
        # === ADMIN: Model Selector ===
        if self.user.is_admin():
            model_selector_layout = QHBoxLayout()
            model_selector_layout.addWidget(QLabel("🎯 Chọn Model:"))
            
            self.model_selector = QComboBox()
            self.model_selector.addItems([
                "XGBoost (Active)",
                "LightGBM",
                "CatBoost",
                "RandomForest",
                "Logistic",
                "NeuralNet",
                "Voting",
                "Stacking"
            ])
            self.model_selector.setStyleSheet("""
                QComboBox {
                    padding: 5px;
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            model_selector_layout.addWidget(self.model_selector)
            model_selector_layout.addStretch()
            main_layout.addLayout(model_selector_layout)
        else:
            self.model_selector = None
        
        # Scroll area để chứa nhiều input
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # === GROUP 1: Thông tin cá nhân ===
        group_personal = self.create_personal_info_group()
        scroll_layout.addWidget(group_personal)
        
        # === GROUP 2: Lịch sử thanh toán ===
        group_payment_history = self.create_payment_history_group()
        scroll_layout.addWidget(group_payment_history)
        
        # === GROUP 3: Chi tiết sao kê ===
        group_billing = self.create_billing_details_group()
        scroll_layout.addWidget(group_billing)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # === BUTTONS ===
        button_layout = QHBoxLayout()
        
        # CRUD Buttons
        self.btnSaveCustomer = QPushButton("💾 Lưu Khách Hàng")
        self.btnSaveCustomer.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnSaveCustomer.clicked.connect(self.save_customer)
        self.btnSaveCustomer.setToolTip("Lưu thông tin khách hàng vào database (Create/Update)")
        button_layout.addWidget(self.btnSaveCustomer)
        
        self.btnDeleteCustomer = QPushButton("🗑️ Xóa Khách Hàng")
        self.btnDeleteCustomer.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btnDeleteCustomer.clicked.connect(self.delete_customer)
        self.btnDeleteCustomer.setToolTip("Xóa khách hàng khỏi database theo CMND")
        button_layout.addWidget(self.btnDeleteCustomer)
        
        self.chkSaveHistory = QCheckBox("Lưu vào lịch sử dự báo")
        self.chkSaveHistory.setChecked(True)
        button_layout.addWidget(self.chkSaveHistory)
        
        button_layout.addStretch()
        
        self.btnClear = QPushButton("Xóa Form")
        self.btnClear.clicked.connect(self.clear_form)
        button_layout.addWidget(self.btnClear)
        
        self.btnPredict = QPushButton("Dự Báo Rủi Ro")
        self.btnPredict.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.btnPredict.clicked.connect(self.on_predict_clicked)
        button_layout.addWidget(self.btnPredict)
        
        # === ADMIN: Compare All Models Button ===
        if self.user.is_admin():
            self.btnCompareAll = QPushButton("📊 So Sánh 8 Models")
            self.btnCompareAll.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            self.btnCompareAll.clicked.connect(self.compare_all_models)
            button_layout.addWidget(self.btnCompareAll)
        
        main_layout.addLayout(button_layout)
        
        # === RESULT DISPLAY ===
        self.result_group = self.create_result_group()
        main_layout.addWidget(self.result_group)
        
        self.setLayout(main_layout)
    
    def create_personal_info_group(self) -> QGroupBox:
        """Tạo GroupBox thông tin cá nhân"""
        group = QGroupBox("📋 THÔNG TIN CÁ NHÂN")
        layout = QFormLayout()
        
        # Customer name (optional)
        self.txtCustomerName = QLineEdit()
        self.txtCustomerName.setPlaceholderText("Tên khách hàng (tùy chọn)")
        layout.addRow("Tên khách hàng:", self.txtCustomerName)
        
        # Customer ID card (optional) + Search Button
        cmnd_layout = QHBoxLayout()
        self.txtCustomerID = QLineEdit()
        self.txtCustomerID.setPlaceholderText("CMND/CCCD (tùy chọn)")
        cmnd_layout.addWidget(self.txtCustomerID)
        
        self.btnSearch = QPushButton("🔍 Tìm kiếm")
        self.btnSearch.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnSearch.clicked.connect(self.search_customer)
        self.btnSearch.setToolTip("Tìm kiếm khách hàng theo CMND/CCCD và tự động điền form")
        cmnd_layout.addWidget(self.btnSearch)
        
        layout.addRow("CMND/CCCD:", cmnd_layout)
        
        # LIMIT_BAL
        self.spnLimitBal = QDoubleSpinBox()
        self.spnLimitBal.setRange(0, 10000000 * self.EXCHANGE_RATE)
        self.spnLimitBal.setValue(50000 * self.EXCHANGE_RATE)  # 40M VND mặc định
        self.spnLimitBal.setToolTip("Hạn mức tín dụng của thẻ")
        layout.addRow("Hạn mức thẻ:", self.spnLimitBal)
        
        # SEX
        self.cmbSex = QComboBox()
        self.cmbSex.addItems(["Nam", "Nữ"])
        layout.addRow("Giới tính:", self.cmbSex)
        
        # EDUCATION
        self.cmbEducation = QComboBox()
        self.cmbEducation.addItems([
            "Cao học",
            "Đại học",
            "Trung học",
            "Khác"
        ])
        self.cmbEducation.setCurrentIndex(1)  # Default: Đại học
        layout.addRow("Trình độ học vấn:", self.cmbEducation)
        
        # MARRIAGE
        self.cmbMarriage = QComboBox()
        self.cmbMarriage.addItems([
            "Kết hôn",
            "Độc thân",
            "Khác"
        ])
        self.cmbMarriage.setCurrentIndex(1)  # Default: Độc thân
        layout.addRow("Tình trạng hôn nhân:", self.cmbMarriage)
        
        # AGE
        self.spnAge = QDoubleSpinBox()
        self.spnAge.setRange(18, 100)
        self.spnAge.setValue(30)
        self.spnAge.setDecimals(0)
        layout.addRow("Tuổi:", self.spnAge)
        
        group.setLayout(layout)
        return group
    
    def create_payment_history_group(self) -> QGroupBox:
        """Tạo GroupBox lịch sử thanh toán với option 12/6 tháng"""
        group = QGroupBox("💳 LỊCH SỬ THANH TOÁN")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        main_layout = QVBoxLayout()
        
        # === Header: RadioButton + Random Button ===
        header_layout = QHBoxLayout()
        
        # RadioButton: Chọn 12 hoặc 6 tháng
        self.rbtn_12months = QRadioButton("12 tháng (Dataset đầy đủ)")
        self.rbtn_6months = QRadioButton("6 tháng (Dataset rút gọn)")
        self.rbtn_12months.setChecked(True)
        
        self.period_group = QButtonGroup()
        self.period_group.addButton(self.rbtn_12months)
        self.period_group.addButton(self.rbtn_6months)
        self.period_group.buttonClicked.connect(self.on_period_changed)
        
        header_layout.addWidget(self.rbtn_12months)
        header_layout.addWidget(self.rbtn_6months)
        header_layout.addStretch()
        
        # Random Button
        self.btnRandomPayments = QPushButton("🎲 Random ngẫu nhiên")
        self.btnRandomPayments.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnRandomPayments.clicked.connect(self.random_payment_history)
        self.btnRandomPayments.setToolTip("Tự động điền giá trị ngẫu nhiên hợp lý cho lịch sử thanh toán")
        header_layout.addWidget(self.btnRandomPayments)
        
        main_layout.addLayout(header_layout)
        
        # === Form Layout cho payment fields ===
        form_layout = QFormLayout()
        
        self.pay_options = [
            "Không sử dụng",
            "Trả đúng hạn",
            "Trễ 1 tháng",
            "Trễ 2 tháng",
            "Trễ 3 tháng",
            "Trễ 4 tháng",
            "Trễ 5 tháng",
            "Trễ 6 tháng",
            "Trễ 7 tháng",
            "Trễ 8 tháng",
            "Trễ 9+ tháng"
        ]
        
        self.pay_combos = {}
        
        # 12 tháng (gần đến xa): Tháng 12 (PAY_0), 11 (PAY_2), ..., 1 (PAY_12)
        self.month_mapping_12 = [
            ('PAY_0', 'Tháng 12 (gần nhất)'),
            ('PAY_2', 'Tháng 11'),
            ('PAY_3', 'Tháng 10'),
            ('PAY_4', 'Tháng 9'),
            ('PAY_5', 'Tháng 8'),
            ('PAY_6', 'Tháng 7'),
            ('PAY_7', 'Tháng 6'),
            ('PAY_8', 'Tháng 5'),
            ('PAY_9', 'Tháng 4'),
            ('PAY_10', 'Tháng 3'),
            ('PAY_11', 'Tháng 2'),
            ('PAY_12', 'Tháng 1 (xa nhất)')
        ]
        
        for pay_field, month_label in self.month_mapping_12:
            cmb = QComboBox()
            cmb.addItems(self.pay_options)
            cmb.setCurrentIndex(1)  # Default: "Trả đúng hạn"
            cmb.setToolTip(f"Trạng thái thanh toán {month_label.lower()}")
            form_layout.addRow(f"{month_label}:", cmb)
            self.pay_combos[pay_field] = cmb
        
        main_layout.addLayout(form_layout)
        group.setLayout(main_layout)
        return group
    
    def on_period_changed(self):
        """Xử lý khi user chuyển đổi giữa 12/6 tháng"""
        is_12months = self.rbtn_12months.isChecked()
        
        # Ẩn/hiện các tháng 7-12
        months_to_toggle = ['PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12']
        
        for pay_field in months_to_toggle:
            combo = self.pay_combos.get(pay_field)
            if combo:
                combo.setVisible(is_12months)
                # Ẩn label tương ứng
                for i in range(combo.parent().layout().count()):
                    item = combo.parent().layout().itemAt(i)
                    if item and item.widget() == combo:
                        # Tìm label tương ứng (là widget trước combo)
                        if i > 0:
                            label_item = combo.parent().layout().itemAt(i - 1)
                            if label_item and label_item.widget():
                                label_item.widget().setVisible(is_12months)
        
        # Tương tự cho billing details
        if hasattr(self, 'bill_amts') and hasattr(self, 'pay_amts'):
            for i in range(6, 12):  # Index 6-11 tương ứng tháng 7-12
                self.bill_amts[i].setVisible(is_12months)
                self.pay_amts[i].setVisible(is_12months)
                # Ẩn labels
                for widget in [self.bill_amts[i], self.pay_amts[i]]:
                    for j in range(widget.parent().layout().count()):
                        item = widget.parent().layout().itemAt(j)
                        if item and item.widget() == widget:
                            if j > 0:
                                label_item = widget.parent().layout().itemAt(j - 1)
                                if label_item and label_item.widget():
                                    label_item.widget().setVisible(is_12months)
    
    def random_payment_history(self):
        """Tự động điền random hợp lý cho lịch sử thanh toán"""
        # Random với logic: càng về trước càng ít khả năng trễ nhiều
        for i, (pay_field, _) in enumerate(self.month_mapping_12):
            combo = self.pay_combos[pay_field]
            
            # Tháng gần: 70% trả đúng hạn, 20% trễ 1-3 tháng, 10% trễ nhiều
            # Tháng xa: 80% trả đúng hạn, 15% trễ 1-2 tháng, 5% trễ nhiều
            if i < 3:  # 3 tháng gần nhất
                weights = [5, 50, 20, 10, 8, 3, 2, 1, 0.5, 0.3, 0.2]
            elif i < 6:  # Tháng 7-10
                weights = [5, 60, 15, 10, 5, 2, 1, 1, 0.5, 0.3, 0.2]
            else:  # Tháng 1-6
                weights = [5, 70, 12, 7, 3, 1, 1, 0.5, 0.3, 0.1, 0.1]
            
            selected_index = random.choices(range(len(self.pay_options)), weights=weights)[0]
            combo.setCurrentIndex(selected_index)
    
    def create_billing_details_group(self) -> QGroupBox:
        """Tạo GroupBox chi tiết sao kê với random button"""
        group = QGroupBox("📊 CHI TIẾT SAO KÊ")
        main_layout = QVBoxLayout()
        
        # === Header: Random Button ===
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.btnRandomBilling = QPushButton("🎲 Random ngẫu nhiên")
        self.btnRandomBilling.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.btnRandomBilling.clicked.connect(self.random_billing_details)
        self.btnRandomBilling.setToolTip("Tự động điền giá trị ngẫu nhiên hợp lý cho số dư và thanh toán")
        header_layout.addWidget(self.btnRandomBilling)
        
        main_layout.addLayout(header_layout)
        
        # === Form Layout ===
        form_layout = QFormLayout()
        
        self.bill_amts = []
        self.pay_amts = []
        
        for i in range(1, 13):
            month_num = 13 - i  # Tháng 12, 11, 10, ..., 1
            month_label = f"Tháng {month_num}"
            if month_num == 12:
                month_label += " (gần nhất)"
            elif month_num == 1:
                month_label += " (xa nhất)"
            
            # BILL_AMT - Số dư sao kê
            spn_bill = QDoubleSpinBox()
            spn_bill.setRange(-1000000 * self.EXCHANGE_RATE, 10000000 * self.EXCHANGE_RATE)
            spn_bill.setValue(0)
            spn_bill.setToolTip(f"Số dư sao kê {month_label.lower()}")
            form_layout.addRow(f"Số dư {month_label}:", spn_bill)
            self.bill_amts.append(spn_bill)
            
            # PAY_AMT - Số tiền đã thanh toán
            spn_pay = QDoubleSpinBox()
            spn_pay.setRange(0, 10000000 * self.EXCHANGE_RATE)
            spn_pay.setValue(0)
            spn_pay.setToolTip(f"Số tiền đã thanh toán {month_label.lower()}")
            form_layout.addRow(f"Thanh toán {month_label}:", spn_pay)
            self.pay_amts.append(spn_pay)
        
        main_layout.addLayout(form_layout)
        group.setLayout(main_layout)
        return group
    
    def random_billing_details(self):
        """Tự động điền random hợp lý cho billing details"""
        limit_bal = self.spnLimitBal.value()
        
        for i in range(12):
            # Bill amount: 0-80% hạn mức
            bill_amt = random.randint(0, int(limit_bal * 0.8))
            self.bill_amts[i].setValue(bill_amt)
            
            # Pay amount: 5-100% của bill amount
            if bill_amt > 0:
                pay_amt = random.randint(int(bill_amt * 0.05), bill_amt)
                self.pay_amts[i].setValue(pay_amt)
            else:
                self.pay_amts[i].setValue(0)
    
    def create_result_group(self) -> QGroupBox:
        """Tạo GroupBox hiển thị kết quả dự báo"""
        group = QGroupBox("📈 KẾT QUẢ DỰ BÁO")
        group.setVisible(False)  # Ẩn ban đầu
        
        layout = QVBoxLayout()
        
        # Label hiển thị nhãn rủi ro
        self.lblRiskLabel = QLabel("Nguy cơ thấp")
        self.lblRiskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_risk = QFont()
        font_risk.setPointSize(20)
        font_risk.setBold(True)
        self.lblRiskLabel.setFont(font_risk)
        self.lblRiskLabel.setStyleSheet("color: green; padding: 20px;")
        layout.addWidget(self.lblRiskLabel)
        
        # Label hiển thị xác suất
        self.lblProbability = QLabel("Xác suất vỡ nợ: 0.0%")
        self.lblProbability.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_prob = QFont()
        font_prob.setPointSize(16)
        self.lblProbability.setFont(font_prob)
        layout.addWidget(self.lblProbability)
        
        group.setLayout(layout)
        return group
    
    def collect_input(self) -> dict:
        """Thu thập input từ form thành dictionary (41 fields) - ĐẢM BẢO ĐÚNG THỨ TỰ"""
        # Parse PAY values (tiếng Việt thuần)
        def parse_pay_value(combo_text):
            """Parse 'Trả đúng hạn' -> 0, 'Trễ 3 tháng' -> 3, 'Không sử dụng' -> -2"""
            pay_map = {
                "Không sử dụng": -2,
                "Trả đúng hạn": 0,
                "Trễ 1 tháng": 1,
                "Trễ 2 tháng": 2,
                "Trễ 3 tháng": 3,
                "Trễ 4 tháng": 4,
                "Trễ 5 tháng": 5,
                "Trễ 6 tháng": 6,
                "Trễ 7 tháng": 7,
                "Trễ 8 tháng": 8,
                "Trễ 9+ tháng": 9
            }
            return pay_map.get(combo_text, 0)
        
        # Parse SEX, EDUCATION, MARRIAGE
        sex_map = {"Nam": 1, "Nữ": 2}
        edu_map = {"Cao học": 1, "Đại học": 2, "Trung học": 3, "Khác": 4}
        mar_map = {"Kết hôn": 1, "Độc thân": 2, "Khác": 3}
        
        # Tạo dict theo ĐÚNG THỨ TỰ model train (FEATURE_NAMES trong preprocess.py)
        # 'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
        # 'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6', 'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12',
        # 'BILL_AMT1', 'BILL_AMT2', ..., 'BILL_AMT12',
        # 'PAY_AMT1', 'PAY_AMT2', ..., 'PAY_AMT12'
        
        is_12months = self.rbtn_12months.isChecked()
        
        input_dict = {}
        
        # 1. Thông tin cá nhân (5 fields) - CHUYỂN ĐỔI VỀ NT$ NẾU CẦN
        limit_bal = self.spnLimitBal.value()
        if self.current_currency == 'VND':
            limit_bal = limit_bal / self.EXCHANGE_RATE  # VND -> NT$
        input_dict['LIMIT_BAL'] = limit_bal
        
        input_dict['SEX'] = sex_map.get(self.cmbSex.currentText(), 1)
        input_dict['EDUCATION'] = edu_map.get(self.cmbEducation.currentText(), 2)
        input_dict['MARRIAGE'] = mar_map.get(self.cmbMarriage.currentText(), 2)
        input_dict['AGE'] = int(self.spnAge.value())
        
        # 2. Payment history - TẤT CẢ 12 tháng (PAY_0, PAY_2-12)
        input_dict['PAY_0'] = parse_pay_value(self.pay_combos['PAY_0'].currentText())
        input_dict['PAY_2'] = parse_pay_value(self.pay_combos['PAY_2'].currentText())
        input_dict['PAY_3'] = parse_pay_value(self.pay_combos['PAY_3'].currentText())
        input_dict['PAY_4'] = parse_pay_value(self.pay_combos['PAY_4'].currentText())
        input_dict['PAY_5'] = parse_pay_value(self.pay_combos['PAY_5'].currentText())
        input_dict['PAY_6'] = parse_pay_value(self.pay_combos['PAY_6'].currentText())
        
        # PAY_7-12 (tùy chọn hoặc điền 0)
        input_dict['PAY_7'] = parse_pay_value(self.pay_combos['PAY_7'].currentText()) if is_12months else 0
        input_dict['PAY_8'] = parse_pay_value(self.pay_combos['PAY_8'].currentText()) if is_12months else 0
        input_dict['PAY_9'] = parse_pay_value(self.pay_combos['PAY_9'].currentText()) if is_12months else 0
        input_dict['PAY_10'] = parse_pay_value(self.pay_combos['PAY_10'].currentText()) if is_12months else 0
        input_dict['PAY_11'] = parse_pay_value(self.pay_combos['PAY_11'].currentText()) if is_12months else 0
        input_dict['PAY_12'] = parse_pay_value(self.pay_combos['PAY_12'].currentText()) if is_12months else 0
        
        # 3. Bill amounts - TẤT CẢ 12 tháng (BILL_AMT1-12) - CHUYỂN ĐỔI VỀ NT$
        for i in range(12):
            bill_val = self.bill_amts[i].value() if is_12months or i < 6 else 0.0
            if self.current_currency == 'VND':
                bill_val = bill_val / self.EXCHANGE_RATE
            input_dict[f'BILL_AMT{i+1}'] = bill_val
        
        # 4. Payment amounts - TẤT CẢ 12 tháng (PAY_AMT1-12) - CHUYỂN ĐỔI VỀ NT$
        for i in range(12):
            pay_val = self.pay_amts[i].value() if is_12months or i < 6 else 0.0
            if self.current_currency == 'VND':
                pay_val = pay_val / self.EXCHANGE_RATE
            input_dict[f'PAY_AMT{i+1}'] = pay_val
        
        return input_dict
    
    def on_predict_clicked(self):
        """Xử lý sự kiện click nút Dự Báo"""
        if not self.ml_service:
            QMessageBox.warning(self, "Lỗi", "Không thể load ML model. Vui lòng train model trước.")
            return
        
        try:
            # Collect input
            input_dict = self.collect_input()
            
            # Debug: In ra input để kiểm tra
            print(f"\n{'='*60}")
            print(f"🔍 DEBUG INPUT:")
            print(f"   Dataset mode: {'12 tháng' if self.rbtn_12months.isChecked() else '6 tháng'}")
            print(f"   Total fields: {len(input_dict)}")
            print(f"   LIMIT_BAL: {input_dict['LIMIT_BAL']}")
            print(f"   PAY_0 (T12): {input_dict['PAY_0']}, PAY_2 (T11): {input_dict['PAY_2']}")
            print(f"   PAY_6 (T7): {input_dict['PAY_6']}, PAY_7 (T6): {input_dict['PAY_7']}")
            print(f"{'='*60}\n")
            
            # Admin: Chọn model từ dropdown
            if self.user.is_admin() and self.model_selector:
                selected_model = self.model_selector.currentText().split()[0]  # Get model name
                print(f"Admin selected model: {selected_model}")
                try:
                    self.ml_service = MLService(model_name=selected_model)
                except Exception as e:
                    QMessageBox.warning(self, "Lỗi", f"Không thể load model {selected_model}: {e}")
                    return
            
            # Predict
            result = self.ml_service.predict_default_risk(input_dict)
            
            # Display result
            self.display_result(result)
            
            # Save to database if checked
            if self.chkSaveHistory.isChecked():
                self.save_prediction_to_db(input_dict, result)
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi dự báo: {str(e)}")
            print(f"Prediction error: {e}")
    
    def display_result(self, result):
        """Hiển thị kết quả dự báo"""
        self.result_group.setVisible(True)
        
        # Update risk label
        risk_label = result.get_risk_label()
        self.lblRiskLabel.setText(risk_label)
        
        # Update color based on risk
        if result.is_high_risk():
            self.lblRiskLabel.setStyleSheet("color: red; padding: 20px; background-color: #ffe6e6; border-radius: 10px;")
        else:
            self.lblRiskLabel.setStyleSheet("color: green; padding: 20px; background-color: #e6ffe6; border-radius: 10px;")
        
        # Update probability
        self.lblProbability.setText(f"Xác suất vỡ nợ: {result.get_probability_percentage()}")
    
    def save_prediction_to_db(self, input_dict, result):
        """Lưu prediction vào database"""
        try:
            # Create customer if has name/ID
            customer_id = None
            customer_name = self.txtCustomerName.text().strip()
            customer_id_card = self.txtCustomerID.text().strip()
            
            if customer_name or customer_id_card:
                customer = Customer(
                    customer_name=customer_name or None,
                    customer_id_card=customer_id_card or None,
                    **input_dict
                )
                customer_id = self.query_service.save_customer(customer)
            
            # Save prediction log
            self.query_service.save_prediction_log(
                customer_id=customer_id,
                model_name=result.model_name,
                predicted_label=result.label,
                probability=result.probability,
                raw_input_dict=input_dict
            )
            
            print("✓ Đã lưu prediction vào database")
        
        except Exception as e:
            print(f"⚠ Không thể lưu vào database: {e}")
    
    def clear_form(self):
        """Xóa toàn bộ form"""
        self.txtCustomerName.clear()
        self.txtCustomerID.clear()
        
        # Reset về VND với giá trị mặc định
        default_limit = 50000 * self.EXCHANGE_RATE  # 40M VND
        self.spnLimitBal.setValue(default_limit)
        
        self.cmbSex.setCurrentIndex(0)
        self.cmbEducation.setCurrentIndex(1)
        self.cmbMarriage.setCurrentIndex(1)
        self.spnAge.setValue(30)
        
        for combo in self.pay_combos.values():
            combo.setCurrentIndex(1)  # "Trả đúng hạn"
        
        for i, spn in enumerate(self.bill_amts):
            spn.setValue(0)
        
        for i, spn in enumerate(self.pay_amts):
            spn.setValue(0)
        
        self.result_group.setVisible(False)
    
    def compare_all_models(self):
        """So sánh 8 models cùng lúc (Admin only)"""
        if not self.user.is_admin():
            return
        
        try:
            # Collect input
            input_dict = self.collect_input()
            
            models = ['XGBoost', 'LightGBM', 'CatBoost', 'RandomForest', 
                      'Logistic', 'NeuralNet', 'Voting', 'Stacking']
            
            results = {}
            errors = []
            
            # Progress dialog
            progress = QMessageBox(self)
            progress.setWindowTitle("Đang so sánh models...")
            progress.setText("Vui lòng đợi trong khi hệ thống chạy 8 models")
            progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress.show()
            
            for model_name in models:
                try:
                    service = MLService(model_name=model_name)
                    result = service.predict_default_risk(input_dict)
                    results[model_name] = result
                    print(f"✓ {model_name}: {result.probability:.2%}")
                except Exception as e:
                    errors.append(f"{model_name}: {str(e)}")
                    results[model_name] = None
                    print(f"✗ {model_name}: {e}")
            
            progress.close()
            
            # Hiển thị kết quả
            self.show_comparison_results(results, errors)
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi so sánh models: {str(e)}")
    
    def show_comparison_results(self, results: dict, errors: list):
        """Hiển thị kết quả so sánh trong dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📊 So Sánh 8 Models")
        dialog.setMinimumSize(800, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("KẾT QUẢ SO SÁNH 8 MODELS")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Model", "Xác suất vỡ nợ", "Nhãn rủi ro", "Trạng thái"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Sắp xếp theo xác suất giảm dần
        sorted_results = sorted(
            [(name, res) for name, res in results.items() if res is not None],
            key=lambda x: x[1].probability,
            reverse=True
        )
        
        table.setRowCount(len(results))
        
        row = 0
        for model_name, result in sorted_results:
            table.setItem(row, 0, QTableWidgetItem(model_name))
            table.setItem(row, 1, QTableWidgetItem(f"{result.probability:.2%}"))
            table.setItem(row, 2, QTableWidgetItem(result.get_risk_label()))
            table.setItem(row, 3, QTableWidgetItem("✅ OK"))
            
            # Màu sắc theo risk
            if result.is_high_risk():
                for col in range(4):
                    table.item(row, col).setBackground(QColor(255, 200, 200))
            else:
                for col in range(4):
                    table.item(row, col).setBackground(QColor(200, 255, 200))
            
            row += 1
        
        # Thêm models bị lỗi
        for error in errors:
            model_name = error.split(':')[0]
            table.setItem(row, 0, QTableWidgetItem(model_name))
            table.setItem(row, 1, QTableWidgetItem("-"))
            table.setItem(row, 2, QTableWidgetItem("-"))
            table.setItem(row, 3, QTableWidgetItem("❌ Error"))
            for col in range(4):
                table.item(row, col).setBackground(QColor(220, 220, 220))
            row += 1
        
        layout.addWidget(table)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def on_currency_changed(self):
        """Xử lý khi user đổi đơn vị tiền tệ"""
        old_currency = self.current_currency
        new_currency = 'VND' if self.rbtn_vnd.isChecked() else 'NT$'
        
        if old_currency == new_currency:
            return
        
        # Chuyển đổi tất cả giá trị
        if new_currency == 'VND':
            # NT$ -> VND: nhân 800
            multiplier = self.EXCHANGE_RATE
        else:
            # VND -> NT$: chia 800
            multiplier = 1 / self.EXCHANGE_RATE
        
        # Convert LIMIT_BAL
        self.spnLimitBal.setValue(self.spnLimitBal.value() * multiplier)
        self.spnLimitBal.setRange(0, 10000000 * (self.EXCHANGE_RATE if new_currency == 'VND' else 1))
        
        # Convert BILL_AMT
        for spn in self.bill_amts:
            spn.setValue(spn.value() * multiplier)
            spn.setRange(-1000000 * (self.EXCHANGE_RATE if new_currency == 'VND' else 1),
                        10000000 * (self.EXCHANGE_RATE if new_currency == 'VND' else 1))
        
        # Convert PAY_AMT
        for spn in self.pay_amts:
            spn.setValue(spn.value() * multiplier)
            spn.setRange(0, 10000000 * (self.EXCHANGE_RATE if new_currency == 'VND' else 1))
        
        self.current_currency = new_currency
    
    def search_customer(self):
        """Tìm kiếm khách hàng theo CMND và tự động điền form"""
        cmnd = self.txtCustomerID.text().strip()
        
        if not cmnd:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số CMND/CCCD để tìm kiếm")
            return
        
        try:
            # Tìm kiếm khách hàng
            customer = self.query_service.get_customer_by_cmnd(cmnd)
            
            if not customer:
                QMessageBox.information(self, "Không tìm thấy", 
                                        f"Không tìm thấy khách hàng với CMND: {cmnd}")
                return
            
            # Điền thông tin vào form
            self.load_customer_data(customer)
            
            QMessageBox.information(self, "Thành công", 
                                    f"Đã tải thông tin khách hàng: {customer.customer_name}")
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tìm kiếm khách hàng: {str(e)}")
    
    def load_customer_data(self, customer: Customer):
        """Tải dữ liệu khách hàng vào form (41 fields)"""
        # Thông tin cá nhân - Database lưu NT$, chuyển sang currency hiện tại
        self.txtCustomerName.setText(customer.customer_name)
        self.txtCustomerID.setText(customer.customer_id_card)
        
        limit_val = customer.LIMIT_BAL
        if self.current_currency == 'VND':
            limit_val *= self.EXCHANGE_RATE
        self.spnLimitBal.setValue(limit_val)
        
        # SEX: 1=Male, 2=Female
        self.cmbSex.setCurrentIndex(0 if customer.SEX == 1 else 1)
        
        # EDUCATION: 1=Cao học, 2=Đại học, 3=Trung học, 4=Khác
        education_map = {1: 0, 2: 1, 3: 2, 4: 3}
        self.cmbEducation.setCurrentIndex(education_map.get(customer.EDUCATION, 3))
        
        # MARRIAGE: 1=Kết hôn, 2=Độc thân, 3=Khác
        marriage_map = {1: 0, 2: 1, 3: 2}
        self.cmbMarriage.setCurrentIndex(marriage_map.get(customer.MARRIAGE, 2))
        
        self.spnAge.setValue(customer.AGE)
        
        # Lịch sử thanh toán (PAY_0, PAY_2-12)
        pay_values = [
            customer.PAY_0, customer.PAY_2, customer.PAY_3, customer.PAY_4,
            customer.PAY_5, customer.PAY_6, customer.PAY_7, customer.PAY_8,
            customer.PAY_9, customer.PAY_10, customer.PAY_11, customer.PAY_12
        ]
        
        for i, (pay_field, _) in enumerate(self.month_mapping_12):
            # Convert PAY value to combo index
            pay_val = pay_values[i]
            if pay_val == -2:
                index = 0  # "Không sử dụng"
            elif pay_val == -1:
                index = 1  # "Trả đúng hạn"
            elif 0 <= pay_val <= 9:
                index = min(pay_val + 2, 10)  # "Trễ X tháng"
            else:
                index = 10  # "Trễ 9+ tháng"
            
            self.pay_combos[pay_field].setCurrentIndex(index)
        
        # Chi tiết sao kê (BILL_AMT1-12, PAY_AMT1-12) - Chuyển đổi sang currency hiện tại
        bill_values = [
            customer.BILL_AMT1, customer.BILL_AMT2, customer.BILL_AMT3,
            customer.BILL_AMT4, customer.BILL_AMT5, customer.BILL_AMT6,
            customer.BILL_AMT7, customer.BILL_AMT8, customer.BILL_AMT9,
            customer.BILL_AMT10, customer.BILL_AMT11, customer.BILL_AMT12
        ]
        
        pay_amt_values = [
            customer.PAY_AMT1, customer.PAY_AMT2, customer.PAY_AMT3,
            customer.PAY_AMT4, customer.PAY_AMT5, customer.PAY_AMT6,
            customer.PAY_AMT7, customer.PAY_AMT8, customer.PAY_AMT9,
            customer.PAY_AMT10, customer.PAY_AMT11, customer.PAY_AMT12
        ]
        
        multiplier = self.EXCHANGE_RATE if self.current_currency == 'VND' else 1
        
        for i in range(12):
            self.bill_amts[i].setValue(bill_values[i] * multiplier)
            self.pay_amts[i].setValue(pay_amt_values[i] * multiplier)
    
    def save_customer(self):
        """Lưu khách hàng vào database (Create/Update)"""
        cmnd = self.txtCustomerID.text().strip()
        name = self.txtCustomerName.text().strip()
        
        if not cmnd:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số CMND/CCCD để lưu khách hàng")
            return
        
        if not name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên khách hàng")
            return
        
        try:
            # Thu thập dữ liệu từ form
            input_dict = self.collect_input()
            
            # Tạo Customer object (đã convert về NT$)
            sex_map = {"Nam": 1, "Nữ": 2}
            edu_map = {"Cao học": 1, "Đại học": 2, "Trung học": 3, "Khác": 4}
            mar_map = {"Kết hôn": 1, "Độc thân": 2, "Khác": 3}
            
            customer = Customer(
                customer_name=name,
                customer_id_card=cmnd,
                LIMIT_BAL=input_dict['LIMIT_BAL'],
                SEX=input_dict['SEX'],
                EDUCATION=input_dict['EDUCATION'],
                MARRIAGE=input_dict['MARRIAGE'],
                AGE=input_dict['AGE'],
                PAY_0=input_dict['PAY_0'],
                PAY_2=input_dict['PAY_2'],
                PAY_3=input_dict['PAY_3'],
                PAY_4=input_dict['PAY_4'],
                PAY_5=input_dict['PAY_5'],
                PAY_6=input_dict['PAY_6'],
                PAY_7=input_dict['PAY_7'],
                PAY_8=input_dict['PAY_8'],
                PAY_9=input_dict['PAY_9'],
                PAY_10=input_dict['PAY_10'],
                PAY_11=input_dict['PAY_11'],
                PAY_12=input_dict['PAY_12'],
                BILL_AMT1=input_dict['BILL_AMT1'],
                BILL_AMT2=input_dict['BILL_AMT2'],
                BILL_AMT3=input_dict['BILL_AMT3'],
                BILL_AMT4=input_dict['BILL_AMT4'],
                BILL_AMT5=input_dict['BILL_AMT5'],
                BILL_AMT6=input_dict['BILL_AMT6'],
                BILL_AMT7=input_dict['BILL_AMT7'],
                BILL_AMT8=input_dict['BILL_AMT8'],
                BILL_AMT9=input_dict['BILL_AMT9'],
                BILL_AMT10=input_dict['BILL_AMT10'],
                BILL_AMT11=input_dict['BILL_AMT11'],
                BILL_AMT12=input_dict['BILL_AMT12'],
                PAY_AMT1=input_dict['PAY_AMT1'],
                PAY_AMT2=input_dict['PAY_AMT2'],
                PAY_AMT3=input_dict['PAY_AMT3'],
                PAY_AMT4=input_dict['PAY_AMT4'],
                PAY_AMT5=input_dict['PAY_AMT5'],
                PAY_AMT6=input_dict['PAY_AMT6'],
                PAY_AMT7=input_dict['PAY_AMT7'],
                PAY_AMT8=input_dict['PAY_AMT8'],
                PAY_AMT9=input_dict['PAY_AMT9'],
                PAY_AMT10=input_dict['PAY_AMT10'],
                PAY_AMT11=input_dict['PAY_AMT11'],
                PAY_AMT12=input_dict['PAY_AMT12']
            )
            
            # Kiểm tra CMND đã tồn tại chưa
            existing = self.query_service.get_customer_by_cmnd(cmnd)
            
            if existing:
                # Update
                reply = QMessageBox.question(
                    self, 'Xác nhận',
                    f'CMND {cmnd} đã tồn tại. Bạn có muốn cập nhật thông tin không?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    success = self.query_service.update_customer(cmnd, customer)
                    if success:
                        QMessageBox.information(self, "Thành công", 
                                                f"Đã cập nhật thông tin khách hàng: {name}")
            else:
                # Create
                customer_id = self.query_service.save_customer(customer)
                if customer_id:
                    QMessageBox.information(self, "Thành công", 
                                            f"Đã lưu khách hàng mới: {name} (ID: {customer_id})")
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu khách hàng: {str(e)}")
    
    def delete_customer(self):
        """Xóa khách hàng khỏi database"""
        cmnd = self.txtCustomerID.text().strip()
        
        if not cmnd:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số CMND/CCCD để xóa khách hàng")
            return
        
        try:
            # Kiểm tra tồn tại
            customer = self.query_service.get_customer_by_cmnd(cmnd)
            
            if not customer:
                QMessageBox.information(self, "Không tìm thấy", 
                                        f"Không tìm thấy khách hàng với CMND: {cmnd}")
                return
            
            # Xác nhận xóa
            reply = QMessageBox.question(
                self, 'Xác nhận xóa',
                f'Bạn có chắc chắn muốn xóa khách hàng:\n\n'
                f'Tên: {customer.customer_name}\n'
                f'CMND: {cmnd}\n\n'
                f'Thao tác này KHÔNG THỂ hoàn tác!',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.query_service.delete_customer(cmnd)
                if success:
                    QMessageBox.information(self, "Thành công", 
                                            f"Đã xóa khách hàng: {customer.customer_name}")
                    self.clear_form()
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa khách hàng: {str(e)}")
