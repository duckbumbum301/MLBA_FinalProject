from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit
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
    from .integration import get_db_connector, get_query_service, get_ml_service
except Exception:
    from integration import get_db_connector, get_query_service, get_ml_service
import json

class PredictionTab(QWidget):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.model_selector = None
        self.result_label = QLabel()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        if self.user.is_admin():
            self.model_selector = QComboBox()
            self.model_selector.addItems([
                'XGBoost (Active)',
                'LightGBM',
                'CatBoost',
                'Neural Network',
                'Voting Ensemble',
                'Stacking Ensemble',
                'Logistic'
            ])
            header.addWidget(self.model_selector)
            self.btn_compare_all = QPushButton('So Sánh 8 Models')
            self.btn_compare_all.clicked.connect(self.compare_all_models)
            header.addWidget(self.btn_compare_all)
        layout.addLayout(header)
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText('Nhập dữ liệu khách hàng (JSON hoặc dạng đơn giản)')
        layout.addWidget(self.input_area)
        actions = QHBoxLayout()
        self.btn_predict = QPushButton('Dự Báo')
        self.btn_predict.clicked.connect(self.on_predict_clicked)
        actions.addWidget(self.btn_predict)
        actions.addStretch()
        layout.addLayout(actions)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setText('Kết quả sẽ hiển thị tại đây')
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_predict_clicked(self):
        if self.user.is_admin() and self.model_selector is not None:
            model_name = self.model_selector.currentText().split()[0]
        else:
            model_name = 'XGBoost'
        raw_text = self.input_area.toPlainText().strip()
        input_dict = {}
        if raw_text:
            try:
                input_dict = json.loads(raw_text)
            except Exception:
                input_dict = {}
        input_dict['user_id'] = self.user.id
        ml = get_ml_service(model_name=model_name)
        result = ml.predict_default_risk(input_dict)
        self.result_label.setText(f"{result.get_risk_label()} - {result.get_probability_percentage()}")
        try:
            db = get_db_connector()
            qs = get_query_service(db)
            qs.save_prediction_log(
                customer_id=None,
                model_name=result.model_name,
                predicted_label=result.label,
                probability=result.probability,
                raw_input_dict=input_dict
            )
            db.close()
        except Exception:
            pass

    def compare_all_models(self):
        self.result_label.setText('So sánh 8 models: XGBoost, LightGBM, CatBoost, NN, Voting, Stacking, Logistic, RF')
