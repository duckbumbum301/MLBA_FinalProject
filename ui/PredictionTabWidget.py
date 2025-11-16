"""
PredictionTabWidget
Tab Dự Báo Rủi Ro với 41 trường input (12 tháng lịch sử) và hiển thị kết quả
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QCheckBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.customer import Customer
from services.ml_service import MLService
from services.query_service import QueryService


class PredictionTabWidget(QWidget):
    """
    Widget cho Tab Dự Báo Rủi Ro
    Chứa 41 trường input (12 tháng lịch sử) và hiển thị kết quả dự báo
    """
    
    def __init__(self, query_service: QueryService):
        super().__init__()
        self.query_service = query_service
        
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
        
        # Customer ID card (optional)
        self.txtCustomerID = QLineEdit()
        self.txtCustomerID.setPlaceholderText("CMND/CCCD (tùy chọn)")
        layout.addRow("CMND/CCCD:", self.txtCustomerID)
        
        # LIMIT_BAL
        self.spnLimitBal = QDoubleSpinBox()
        self.spnLimitBal.setRange(0, 10000000)
        self.spnLimitBal.setValue(50000)
        self.spnLimitBal.setSuffix(" NT$")
        layout.addRow("Hạn mức thẻ (LIMIT_BAL):", self.spnLimitBal)
        
        # SEX
        self.cmbSex = QComboBox()
        self.cmbSex.addItems(["1 - Nam", "2 - Nữ"])
        layout.addRow("Giới tính (SEX):", self.cmbSex)
        
        # EDUCATION
        self.cmbEducation = QComboBox()
        self.cmbEducation.addItems([
            "1 - Cao học",
            "2 - Đại học",
            "3 - Trung học",
            "4 - Khác"
        ])
        self.cmbEducation.setCurrentIndex(1)  # Default: Đại học
        layout.addRow("Trình độ (EDUCATION):", self.cmbEducation)
        
        # MARRIAGE
        self.cmbMarriage = QComboBox()
        self.cmbMarriage.addItems([
            "1 - Kết hôn",
            "2 - Độc thân",
            "3 - Khác"
        ])
        self.cmbMarriage.setCurrentIndex(1)  # Default: Độc thân
        layout.addRow("Hôn nhân (MARRIAGE):", self.cmbMarriage)
        
        # AGE
        self.spnAge = QDoubleSpinBox()
        self.spnAge.setRange(18, 100)
        self.spnAge.setValue(30)
        self.spnAge.setDecimals(0)
        layout.addRow("Tuổi (AGE):", self.spnAge)
        
        group.setLayout(layout)
        return group
    
    def create_payment_history_group(self) -> QGroupBox:
        """Tạo GroupBox lịch sử thanh toán (PAY_0, PAY_2-12) - 12 tháng"""
        group = QGroupBox("💳 LỊCH SỬ THANH TOÁN (12 tháng)")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QFormLayout()
        
        pay_options = [
            "-2 - Không sử dụng",
            "-1 - Trả đúng hạn",
            "0 - Trả đúng hạn",
            "1 - Trễ 1 tháng",
            "2 - Trễ 2 tháng",
            "3 - Trễ 3 tháng",
            "4 - Trễ 4 tháng",
            "5 - Trễ 5 tháng",
            "6 - Trễ 6 tháng",
            "7 - Trễ 7 tháng",
            "8 - Trễ 8 tháng",
            "9 - Trễ 9+ tháng"
        ]
        
        self.pay_combos = {}
        
        # 12 tháng: PAY_0 (tháng 12), PAY_2 (tháng 11), ..., PAY_12 (tháng 1)
        month_labels = [
            ('PAY_0', 'Tháng 12'),
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
            ('PAY_12', 'Tháng 1')
        ]
        
        for pay_field, month_label in month_labels:
            cmb = QComboBox()
            cmb.addItems(pay_options)
            cmb.setCurrentIndex(2)  # Default: "0 - Trả đúng hạn"
            layout.addRow(f"{pay_field} ({month_label}):", cmb)
            self.pay_combos[pay_field] = cmb
        
        group.setLayout(layout)
        return group
    
    def create_billing_details_group(self) -> QGroupBox:
        """Tạo GroupBox chi tiết sao kê (BILL_AMT và PAY_AMT) - 12 tháng"""
        group = QGroupBox("📊 CHI TIẾT SAO KÊ (12 tháng)")
        layout = QFormLayout()
        
        self.bill_amts = []
        self.pay_amts = []
        
        # 12 tháng: BILL_AMT1 (tháng 12), ..., BILL_AMT12 (tháng 1)
        for i in range(1, 13):
            month_label = 13 - i  # Tháng 12, 11, 10, ..., 1
            
            # BILL_AMT
            spn_bill = QDoubleSpinBox()
            spn_bill.setRange(-1000000, 10000000)
            spn_bill.setValue(0)
            spn_bill.setSuffix(" NT$")
            layout.addRow(f"Số dư sao kê tháng {month_label} (BILL_AMT{i}):", spn_bill)
            self.bill_amts.append(spn_bill)
            
            # PAY_AMT
            spn_pay = QDoubleSpinBox()
            spn_pay.setRange(0, 10000000)
            spn_pay.setValue(0)
            spn_pay.setSuffix(" NT$")
            layout.addRow(f"Số tiền thanh toán tháng {month_label} (PAY_AMT{i}):", spn_pay)
            self.pay_amts.append(spn_pay)
        
        group.setLayout(layout)
        return group
    
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
        """Thu thập input từ form thành dictionary (41 fields)"""
        # Parse PAY values
        def parse_pay_value(combo_text):
            """Parse '-1 - Trả đúng hạn' -> -1"""
            return int(combo_text.split(' - ')[0])
        
        input_dict = {
            'LIMIT_BAL': self.spnLimitBal.value(),
            'SEX': int(self.cmbSex.currentText().split(' - ')[0]),
            'EDUCATION': int(self.cmbEducation.currentText().split(' - ')[0]),
            'MARRIAGE': int(self.cmbMarriage.currentText().split(' - ')[0]),
            'AGE': int(self.spnAge.value()),
            
            # Payment history - 12 months
            'PAY_0': parse_pay_value(self.pay_combos['PAY_0'].currentText()),
            'PAY_2': parse_pay_value(self.pay_combos['PAY_2'].currentText()),
            'PAY_3': parse_pay_value(self.pay_combos['PAY_3'].currentText()),
            'PAY_4': parse_pay_value(self.pay_combos['PAY_4'].currentText()),
            'PAY_5': parse_pay_value(self.pay_combos['PAY_5'].currentText()),
            'PAY_6': parse_pay_value(self.pay_combos['PAY_6'].currentText()),
            'PAY_7': parse_pay_value(self.pay_combos['PAY_7'].currentText()),
            'PAY_8': parse_pay_value(self.pay_combos['PAY_8'].currentText()),
            'PAY_9': parse_pay_value(self.pay_combos['PAY_9'].currentText()),
            'PAY_10': parse_pay_value(self.pay_combos['PAY_10'].currentText()),
            'PAY_11': parse_pay_value(self.pay_combos['PAY_11'].currentText()),
            'PAY_12': parse_pay_value(self.pay_combos['PAY_12'].currentText()),
            
            # Bill amounts - 12 months
            'BILL_AMT1': self.bill_amts[0].value(),
            'BILL_AMT2': self.bill_amts[1].value(),
            'BILL_AMT3': self.bill_amts[2].value(),
            'BILL_AMT4': self.bill_amts[3].value(),
            'BILL_AMT5': self.bill_amts[4].value(),
            'BILL_AMT6': self.bill_amts[5].value(),
            'BILL_AMT7': self.bill_amts[6].value(),
            'BILL_AMT8': self.bill_amts[7].value(),
            'BILL_AMT9': self.bill_amts[8].value(),
            'BILL_AMT10': self.bill_amts[9].value(),
            'BILL_AMT11': self.bill_amts[10].value(),
            'BILL_AMT12': self.bill_amts[11].value(),
            
            # Payment amounts - 12 months
            'PAY_AMT1': self.pay_amts[0].value(),
            'PAY_AMT2': self.pay_amts[1].value(),
            'PAY_AMT3': self.pay_amts[2].value(),
            'PAY_AMT4': self.pay_amts[3].value(),
            'PAY_AMT5': self.pay_amts[4].value(),
            'PAY_AMT6': self.pay_amts[5].value(),
            'PAY_AMT7': self.pay_amts[6].value(),
            'PAY_AMT8': self.pay_amts[7].value(),
            'PAY_AMT9': self.pay_amts[8].value(),
            'PAY_AMT10': self.pay_amts[9].value(),
            'PAY_AMT11': self.pay_amts[10].value(),
            'PAY_AMT12': self.pay_amts[11].value(),
        }
        
        return input_dict
    
    def on_predict_clicked(self):
        """Xử lý sự kiện click nút Dự Báo"""
        if not self.ml_service:
            QMessageBox.warning(self, "Lỗi", "Không thể load ML model. Vui lòng train model trước.")
            return
        
        try:
            # Collect input
            input_dict = self.collect_input()
            
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
        self.spnLimitBal.setValue(50000)
        self.cmbSex.setCurrentIndex(0)
        self.cmbEducation.setCurrentIndex(1)
        self.cmbMarriage.setCurrentIndex(1)
        self.spnAge.setValue(30)
        
        for combo in self.pay_combos.values():
            combo.setCurrentIndex(2)
        
        for spn in self.bill_amts + self.pay_amts:
            spn.setValue(0)
        
        self.result_group.setVisible(False)
