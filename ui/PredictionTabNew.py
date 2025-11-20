"""
PredictionTabWidget
Tab Dự Báo Rủi Ro với 41 trường input (12 tháng lịch sử) và hiển thị kết quả
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QGridLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QCheckBox, QMessageBox, QScrollArea, QRadioButton, QButtonGroup,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QApplication, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon
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
    
    prediction_logged = pyqtSignal()

    def __init__(self, user: User, query_service: QueryService):
        super().__init__()
        self.user = user
        self.query_service = query_service
        self.current_currency = 'VND'  # Mặc định VND
        try:
            self.random_icon = QIcon(str(Path(__file__).resolve().parent / 'images' / 'random.png'))
        except Exception:
            self.random_icon = QIcon()
        self._original_customer = None
        
        # Init ML Service (ưu tiên LightGBM cho tất cả vai trò)
        try:
            self.ml_service = MLService(model_name='LightGBM')
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
        
        self.model_selector = None
        
        # Scroll area để chứa nhiều input
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(12,12,12,12)
        scroll_layout.setSpacing(16)
        
        # === GROUP 1: Thông tin cá nhân ===
        group_personal = self.create_personal_info_group()
        scroll_layout.addWidget(group_personal)
        
        # === GROUP 2+3: Đặt hai card nằm cạnh nhau ===
        group_payment_history = self.create_payment_history_group()
        group_billing = self.create_billing_details_group()

        group_payment_history.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        group_billing.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        row_layout = QHBoxLayout(); row_layout.setSpacing(16)
        row_layout.addWidget(group_payment_history)
        row_layout.addWidget(group_billing)
        row_layout.setStretch(0,1); row_layout.setStretch(1,1)
        scroll_layout.addLayout(row_layout)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # === BUTTONS ===
        button_layout = QHBoxLayout(); button_layout.setSpacing(12)
        
        # CRUD Buttons
        self.btnSaveCustomer = QPushButton("💾 Lưu Khách Hàng")
        self.btnSaveCustomer.setObjectName('Primary')
        self.btnSaveCustomer.clicked.connect(self.save_customer)
        self.btnSaveCustomer.setToolTip("Lưu thông tin khách hàng vào database (Create/Update)")
        button_layout.addWidget(self.btnSaveCustomer)

        self.chkForceCreate = QCheckBox("Tạo bản ghi mới")
        self.chkForceCreate.setToolTip("Luôn tạo khách hàng mới, không cập nhật khách cũ")
        button_layout.addWidget(self.chkForceCreate)
        
        self.btnDeleteCustomer = QPushButton("🗑️ Xóa Khách Hàng")
        self.btnDeleteCustomer.setObjectName('Danger')
        self.btnDeleteCustomer.clicked.connect(self.delete_customer)
        self.btnDeleteCustomer.setToolTip("Xóa khách hàng khỏi database theo CMND")
        button_layout.addWidget(self.btnDeleteCustomer)

        self.btnEditToggle = QPushButton("✏️ Chỉnh sửa")
        self.btnEditToggle.setObjectName('Secondary')
        self.btnEditToggle.setToolTip("Chỉnh sửa lịch sử thanh toán và chi tiết sao kê")
        self.btnEditToggle.clicked.connect(self.enable_edit_mode)
        button_layout.addWidget(self.btnEditToggle)
        
        self.btnRestore = QPushButton("↩️ Khôi phục")
        self.btnRestore.setObjectName('Secondary')
        self.btnRestore.setToolTip("Khôi phục dữ liệu trước khi chỉnh sửa và khóa lại")
        self.btnRestore.clicked.connect(self.restore_original_data)
        button_layout.addWidget(self.btnRestore)
        
        self.chkSaveHistory = QCheckBox("Lưu vào lịch sử dự báo")
        self.chkSaveHistory.setChecked(True)
        button_layout.addWidget(self.chkSaveHistory)
        
        button_layout.addStretch()
        
        self.btnClear = QPushButton("Xóa Form")
        self.btnClear.setObjectName('Secondary')
        self.btnClear.clicked.connect(self.clear_form)
        button_layout.addWidget(self.btnClear)
        
        self.btnPredict = QPushButton("Dự Báo Rủi Ro")
        self.btnPredict.setObjectName('Primary')
        self.btnPredict.clicked.connect(self.on_predict_clicked)
        button_layout.addWidget(self.btnPredict)
        
        # === ADMIN: Compare All Models Button ===
        if self.user.is_admin():
            self.btnCompareAll = QPushButton("📊 So sánh 8 mô hình")
            self.btnCompareAll.setObjectName('Secondary')
            self.btnCompareAll.clicked.connect(self.compare_all_models)
            button_layout.addWidget(self.btnCompareAll)
        
        main_layout.addLayout(button_layout)
        
        # === RESULT DISPLAY ===
        self.result_group = self.create_result_group()
        main_layout.addWidget(self.result_group)
        
        self.setLayout(main_layout)
    
    def create_personal_info_group(self) -> QGroupBox:
        """Tạo GroupBox thông tin cá nhân"""
        group = QGroupBox("")
        main_layout = QVBoxLayout()
        header = QLabel("THÔNG TIN CÁ NHÂN")
        header.setObjectName('SectionHeader')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.addWidget(header)
        layout = QFormLayout()
        layout.setHorizontalSpacing(12); layout.setVerticalSpacing(8)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        # Customer name (optional)
        self.txtCustomerName = QLineEdit()
        self.txtCustomerName.setPlaceholderText("Tên khách hàng (tùy chọn)")
        layout.addRow("Tên khách hàng:", self.txtCustomerName)
        
        # Customer ID card (optional) + Search Button
        cmnd_layout = QHBoxLayout()
        self.txtCustomerID = QLineEdit()
        self.txtCustomerID.setPlaceholderText("CMND/CCCD (tùy chọn)")
        cmnd_layout.addWidget(self.txtCustomerID)
        
        self.btnSearch = QPushButton("Tìm kiếm")
        self.btnSearch.setObjectName('Secondary')
        self.btnSearch.setStyleSheet("")
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
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def create_payment_history_group(self) -> QGroupBox:
        """Tạo GroupBox lịch sử thanh toán với option 12/6 tháng"""
        group = QGroupBox("")
        group.setStyleSheet(
            "QGroupBox { background: #f7f9fc; font-weight: bold; border: 1px solid #dfe6ee; border-radius: 10px; }"
        )
        main_layout = QVBoxLayout()
        header = QLabel("LỊCH SỬ THANH TOÁN")
        header.setObjectName('SectionHeader')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.addWidget(header)
        
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
        self.btnRandomPayments = QPushButton("\u00A0\u00A0Random ngẫu nhiên")
        self.btnRandomPayments.setObjectName('Secondary')
        try:
            self.btnRandomPayments.setIcon(self.random_icon)
            self.btnRandomPayments.setIconSize(QSize(20,20))
        except Exception:
            pass
        self.btnRandomPayments.clicked.connect(self.random_payment_history)
        self.btnRandomPayments.setToolTip("Tự động điền giá trị ngẫu nhiên hợp lý cho lịch sử thanh toán")
        header_layout.addWidget(self.btnRandomPayments)
        
        main_layout.addLayout(header_layout)
        
        # === Form Layout cho payment fields ===
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(12); form_layout.setVerticalSpacing(8)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
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
            cmb = QComboBox(); cmb.setMinimumWidth(180)
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
        
        # Tương tự cho billing details (grid layout: có label riêng)
        if hasattr(self, 'bill_amts') and hasattr(self, 'pay_amts') and hasattr(self, 'bill_labels') and hasattr(self, 'pay_labels'):
            for i in range(6, 12):  # Index 6-11 tương ứng tháng 7-12
                for w in [self.bill_amts[i], self.pay_amts[i], self.bill_labels[i], self.pay_labels[i]]:
                    w.setVisible(is_12months)
    
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
        group = QGroupBox("")
        main_layout = QVBoxLayout()
        group.setStyleSheet(
            "QGroupBox { background: #f7f9fc; font-weight: bold; border: 1px solid #dfe6ee; border-radius: 10px; }"
        )
        header = QLabel("CHI TIẾT SAO KÊ")
        header.setObjectName('SectionHeader')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.addWidget(header)
        
        # === Header: Random Button ===
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.btnRandomBilling = QPushButton("\u00A0\u00A0Random ngẫu nhiên")
        self.btnRandomBilling.setObjectName('Secondary')
        try:
            self.btnRandomBilling.setIcon(self.random_icon)
            self.btnRandomBilling.setIconSize(QSize(20,20))
        except Exception:
            pass
        self.btnRandomBilling.clicked.connect(self.random_billing_details)
        self.btnRandomBilling.setToolTip("Tự động điền giá trị ngẫu nhiên hợp lý cho số dư và thanh toán")
        header_layout.addWidget(self.btnRandomBilling)
        
        main_layout.addLayout(header_layout)
        
        # === Grid Layout: 4 cột (Label Bill, Spin Bill, Label Pay, Spin Pay) ===
        grid = QGridLayout()
        grid.setHorizontalSpacing(12); grid.setVerticalSpacing(8)
        grid.setContentsMargins(0,0,0,0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 0)
        
        self.bill_amts = []
        self.pay_amts = []
        
        for i in range(1, 13):
            month_num = 13 - i  # Tháng 12, 11, 10, ..., 1
            month_label = f"Tháng {month_num}"
            if month_num == 12:
                month_label += " (gần nhất)"
            elif month_num == 1:
                month_label += " (xa nhất)"
            
            # Hàng: [Label Bill][Spin Bill]  [Label Pay][Spin Pay]
            lbl_bill = QLabel(f"Số dư {month_label}:")
            lbl_bill.setAlignment(Qt.AlignmentFlag.AlignRight)
            spn_bill = QDoubleSpinBox(); spn_bill.setFixedWidth(160)
            spn_bill.setRange(-1000000 * self.EXCHANGE_RATE, 10000000 * self.EXCHANGE_RATE)
            spn_bill.setValue(0)
            spn_bill.setToolTip(f"Số dư sao kê {month_label.lower()}")
            self.bill_amts.append(spn_bill)

            lbl_pay = QLabel(f"Thanh toán {month_label}:")
            lbl_pay.setAlignment(Qt.AlignmentFlag.AlignRight)
            spn_pay = QDoubleSpinBox(); spn_pay.setFixedWidth(160)
            spn_pay.setRange(0, 10000000 * self.EXCHANGE_RATE)
            spn_pay.setValue(0)
            spn_pay.setToolTip(f"Số tiền đã thanh toán {month_label.lower()}")
            self.pay_amts.append(spn_pay)
            row_index = i - 1
            grid.addWidget(lbl_bill, row_index, 0)
            grid.addWidget(spn_bill, row_index, 1)
            grid.addWidget(lbl_pay, row_index, 2)
            grid.addWidget(spn_pay, row_index, 3)
        
        main_layout.addLayout(grid)
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
        group = QGroupBox("")
        group.setVisible(False)  # Ẩn ban đầu
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)
        
        header = QLabel("KẾT QUẢ DỰ BÁO")
        header.setObjectName('SectionHeader')
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        
        # Label hiển thị mức rủi ro (tier)
        self.lblRiskLabel = QLabel("Trung bình")
        self.lblRiskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_risk = QFont()
        font_risk.setPointSize(24)
        font_risk.setBold(True)
        self.lblRiskLabel.setFont(font_risk)
        self.lblRiskLabel.setStyleSheet("padding: 20px;")
        layout.addWidget(self.lblRiskLabel)
        
        # Label hiển thị xác suất
        self.lblProbability = QLabel("Xác suất vỡ nợ: 0.0%")
        self.lblProbability.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_prob = QFont()
        font_prob.setPointSize(18)
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
        
        tier_label = result.get_risk_tier()
        self.lblRiskLabel.setText(tier_label)
        prob_text = f"Xác suất vỡ nợ: {result.get_probability_percentage()}"
        self.lblProbability.setText(prob_text)
        if tier_label in ("Rất thấp", "Thấp"):
            self.lblRiskLabel.setStyleSheet("color: #27AE60; padding: 20px; background-color: #eaf6ed; border-radius: 10px;")
            self.lblProbability.setStyleSheet("color: #27AE60; padding: 10px; background-color: #eaf6ed; border-radius: 10px;")
        elif tier_label == "Trung bình":
            self.lblRiskLabel.setStyleSheet("color: #DAA520; padding: 20px; background-color: #fff5cc; border-radius: 10px;")
            self.lblProbability.setStyleSheet("color: #DAA520; padding: 10px; background-color: #fff5cc; border-radius: 10px;")
        else:
            self.lblRiskLabel.setStyleSheet("color: #EB5757; padding: 20px; background-color: #fdecef; border-radius: 10px;")
            self.lblProbability.setStyleSheet("color: #EB5757; padding: 10px; background-color: #fdecef; border-radius: 10px;")
    
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
                raw_input_dict=input_dict,
                user_id=getattr(self.user, 'id', None)
            )
            try:
                self.prediction_logged.emit()
            except Exception:
                pass
            
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
        self.set_edit_mode(True)
        self._original_customer = None

    def set_edit_mode(self, enabled: bool):
        # Payment history combos
        for cmb in self.pay_combos.values():
            cmb.setEnabled(enabled)
        # Billing amounts and payment amounts
        for spn in self.bill_amts:
            spn.setEnabled(enabled)
        for spn in self.pay_amts:
            spn.setEnabled(enabled)
        # Random buttons
        if hasattr(self, 'btnRandomPayments'):
            self.btnRandomPayments.setEnabled(enabled)
        if hasattr(self, 'btnRandomBilling'):
            self.btnRandomBilling.setEnabled(enabled)
        # Save button
        if hasattr(self, 'btnSaveCustomer'):
            self.btnSaveCustomer.setEnabled(enabled)
        # Personal info fields
        if hasattr(self, 'spnLimitBal'):
            self.spnLimitBal.setEnabled(enabled)
        if hasattr(self, 'cmbSex'):
            self.cmbSex.setEnabled(enabled)
        if hasattr(self, 'cmbEducation'):
            self.cmbEducation.setEnabled(enabled)
        if hasattr(self, 'cmbMarriage'):
            self.cmbMarriage.setEnabled(enabled)
        if hasattr(self, 'spnAge'):
            self.spnAge.setEnabled(enabled)

    def enable_edit_mode(self):
        self.set_edit_mode(True)

    def restore_original_data(self):
        if self._original_customer:
            self.load_customer_data(self._original_customer)
            self.set_edit_mode(False)
    
    def compare_all_models(self):
        """So sánh 8 models với DEMO labels"""
        print("🟢🟢🟢 compare_all_models NEW VERSION CALLED! 🟢🟢🟢")
        
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QProgressDialog, QApplication
        from PyQt6.QtGui import QColor, QFont
        from PyQt6.QtCore import Qt
        
        # Collect input
        input_dict = self.collect_input()
        
        # Models
        TRAINED_MODELS = {'XGBoost', 'LightGBM', 'LogisticRegression'}
        ALL_MODELS = ['LightGBM', 'XGBoost', 'LogisticRegression', 'CatBoost', 'RandomForest', 'NeuralNet', 'Voting', 'Stacking']
        
        # Progress dialog
        progress = QProgressDialog("Đang so sánh 8 models...", "Hủy", 0, len(ALL_MODELS), self)
        progress.setWindowTitle("Vui lòng đợi")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        results = []
        for i, display_name in enumerate(ALL_MODELS):
            if progress.wasCanceled():
                break
                
            # Map display name to actual model name
            if display_name == 'Logistic':
                model_name = 'LogisticRegression'
            else:
                model_name = display_name
                
            is_trained = model_name in TRAINED_MODELS
            
            print(f"🔸 Processing {display_name} → {model_name} → is_trained={is_trained}")
            
            if is_trained:
                try:
                    print(f"   → Trying to load {model_name}...")
                    service = MLService(model_name=model_name)
                    res = service.predict_default_risk(input_dict)
                    prob = res.probability
                    risk = res.get_risk_label()
                    status = "✅ Hợp lệ"
                    print(f"   ✓ {display_name}: {prob:.2%}")
                except Exception as e:
                    error_msg = str(e)
                    print(f"   ✗ Error: {error_msg}")
                    
                    # Always mark LogisticRegression error as version issue
                    if "LogisticRegression" in model_name:
                        prob = 0.0
                        risk = "Lỗi sklearn"
                        status = "⚠️ Lỗi version"
                        is_trained = False
                        print(f"   ⚠️ {display_name}: Lỗi version sklearn - model cần train lại")
                    else:
                        prob = 0.0
                        risk = "Lỗi"
                        status = "❌ Lỗi"
                        is_trained = False
            else:
                prob = 0.0064
                risk = "Nguy cơ thấp"
                status = "🔸 DEMO"
                print(f"   🔸 {display_name}: DEMO model")
            
            results.append({
                'name': display_name,
                'prob': prob,
                'risk': risk,
                'status': status,
                'is_trained': is_trained  # This determines if (DEMO) label is added
            })
            
            progress.setValue(i + 1)
            QApplication.processEvents()
        
        progress.close()

        # Debug: In toàn bộ kết quả trước khi show dialog
        print("===== DEBUG: KẾT QUẢ SO SÁNH 8 MÔ HÌNH =====")
        for r in results:
            print(f"Model: {r['name']}, prob: {r['prob']}, risk: {r['risk']}, status: {r['status']}, is_trained: {r['is_trained']}")
        print("=============================================")

        # Sort by probability descending
        results.sort(key=lambda x: x['prob'], reverse=True)

        # Show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ SO SÁNH 8 MÔ HÌNH MỚI")
        dialog.setMinimumSize(900, 600)

        layout = QVBoxLayout(dialog)

        title = QLabel("🎯 KẾT QUẢ SO SÁNH 8 MÔ HÌNH (CÓ DEMO LABELS)")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("padding: 15px; background: #e3f2fd; border-radius: 5px;")
        layout.addWidget(title)
        
        table = QTableWidget(len(results), 4)
        table.setHorizontalHeaderLabels(["Mô hình", "Xác suất vỡ nợ", "Nhãn rủi ro", "Trạng thái"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, r in enumerate(results):
            # Add (DEMO) to name if not trained, or (LỖI) if error
            if not r['is_trained']:
                if "Lỗi" in r['status']:
                    model_display = f"{r['name']} ⚠️"  # Error icon for broken models
                else:
                    model_display = f"{r['name']} (DEMO)"  # DEMO label for fake models
            else:
                model_display = r['name']
            
            table.setItem(i, 0, QTableWidgetItem(model_display))
            table.setItem(i, 1, QTableWidgetItem(f"{r['prob']:.2%}"))
            table.setItem(i, 2, QTableWidgetItem(r['risk']))
            table.setItem(i, 3, QTableWidgetItem(r['status']))
            
            # Color
            if r['prob'] >= 0.5:
                color = QColor(255, 200, 200)
            else:
                color = QColor(200, 255, 200)
            
            for col in range(4):
                table.item(i, col).setBackground(color)
        
        layout.addWidget(table)
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setMinimumWidth(150)
        layout.addWidget(close_btn)
        
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
            
            self.load_customer_data(customer)
            self.set_edit_mode(False)
            self._original_customer = customer
            
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
            
            # Kiểm tra CMND đã tồn tại và đang chỉnh trên khách hiện tại
            existing = self.query_service.get_customer_by_cmnd(cmnd)
            is_editing_current = bool(self._original_customer and str(self._original_customer.customer_id_card or '').strip() == cmnd)
            force_create = False
            try:
                force_create = self.chkForceCreate.isChecked()
            except Exception:
                force_create = False
            
            if (existing or is_editing_current) and not force_create:
                # Update
                do_update = True
                if not is_editing_current:
                    reply = QMessageBox.question(
                        self, 'Xác nhận',
                        f'CMND {cmnd} đã tồn tại. Bạn có muốn cập nhật thông tin không?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    do_update = (reply == QMessageBox.StandardButton.Yes)
                
                if do_update:
                    success = self.query_service.update_customer(cmnd, customer)
                    if success:
                        try:
                            updated = self.query_service.get_customer_by_cmnd(cmnd)
                            if updated:
                                QMessageBox.information(self, "Thành công", 
                                                        f"Đã cập nhật khách hàng: {name}\nLIMIT_BAL: {updated.LIMIT_BAL}")
                            else:
                                QMessageBox.information(self, "Thành công", 
                                                        f"Đã cập nhật thông tin khách hàng: {name}")
                        except Exception:
                            QMessageBox.information(self, "Thành công", 
                                                    f"Đã cập nhật thông tin khách hàng: {name}")
                        try:
                            if 'updated' in locals() and updated:
                                self._original_customer = updated
                            self.set_edit_mode(False)
                            if hasattr(self, 'chkForceCreate'):
                                self.chkForceCreate.setChecked(False)
                        except Exception:
                            pass
                    else:
                        QMessageBox.critical(self, "Lỗi", 
                                             "Không thể cập nhật khách hàng vào credit_risk_db. Vui lòng thử lại hoặc kiểm tra kết nối DB.")
                else:
                    QMessageBox.information(self, "Bỏ qua", "Đã hủy cập nhật khách hàng.")
            else:
                # Create
                customer_id = self.query_service.save_customer(customer, strict_insert=force_create)
                if customer_id:
                    try:
                        updated = self.query_service.get_customer_by_cmnd(cmnd)
                        if updated:
                            QMessageBox.information(self, "Thành công", 
                                                    f"Đã lưu khách hàng mới: {name} (ID: {customer_id})\nLIMIT_BAL: {updated.LIMIT_BAL}")
                        else:
                            QMessageBox.information(self, "Thành công", 
                                                    f"Đã lưu khách hàng mới: {name} (ID: {customer_id})")
                    except Exception:
                        QMessageBox.information(self, "Thành công", 
                                                f"Đã lưu khách hàng mới: {name} (ID: {customer_id})")
                    try:
                        if 'updated' in locals() and updated:
                            self._original_customer = updated
                        self.set_edit_mode(False)
                        if hasattr(self, 'chkForceCreate'):
                            self.chkForceCreate.setChecked(False)
                    except Exception:
                        pass
                else:
                    QMessageBox.critical(self, "Lỗi", 
                                         "Không thể lưu khách hàng vào credit_risk_db. Vui lòng thử lại hoặc kiểm tra kết nối DB.")
        
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
