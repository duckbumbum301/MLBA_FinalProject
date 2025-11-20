"""
Dialog để so sánh dự đoán của nhiều models cho cùng 1 khách hàng
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from services.ml_service import MLService


class ModelComparisonDialog(QDialog):
    """Dialog so sánh dự đoán của 8 models"""
    
    # Models that actually exist
    TRAINED_MODELS = {'XGBoost', 'LightGBM', 'LogisticRegression'}
    
    # All models to display
    ALL_MODELS = [
        'LightGBM',
        'XGBoost', 
        'CatBoost',
        'RandomForest',
        'Logistic',
        'NeuralNet',
        'Voting',
        'Stacking'
    ]
    
    def __init__(self, customer_data: Dict[str, Any], parent=None):
        print("🟡 ModelComparisonDialog.__init__() CALLED!")
        print(f"🟡 TRAINED_MODELS = {self.TRAINED_MODELS}")
        print(f"🟡 ALL_MODELS = {self.ALL_MODELS}")
        super().__init__(parent)
        self.customer_data = customer_data
        self.setWindowTitle("☐ So sánh 8 mô hình")
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.run_comparison()
    
    def setup_ui(self):
        """Setup giao diện"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("KẾT QUẢ SO SÁNH 8 MÔ HÌNH")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Mô hình", "Xác suất vỡ nợ", "Nhãn rủi ro", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(len(self.ALL_MODELS))
        layout.addWidget(self.table)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumWidth(150)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        try:
            icon_path = Path(__file__).resolve().parent / 'images' / 'logo.png'
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
    
    def run_comparison(self):
        """Chạy so sánh dự đoán từ các models"""
        results = []
        
        # Model name mapping
        model_name_map = {
            'Logistic': 'LogisticRegression'
        }
        
        for display_name in self.ALL_MODELS:
            # Map display name to actual model name
            model_name = model_name_map.get(display_name, display_name)
            
            # Check if this is a trained model (simple check by name)
            is_trained = model_name in self.TRAINED_MODELS
            print(f"DEBUG: {display_name} → {model_name} → is_trained={is_trained} (TRAINED_MODELS={self.TRAINED_MODELS})")
            
            if is_trained:
                # Run real prediction
                try:
                    ml_service = MLService(model_name=model_name)
                    result = ml_service.predict_default_risk(self.customer_data)
                    probability = result.probability
                    risk_label = result.get_risk_label()
                    status = "✅ Hợp lệ"
                    print(f"✓ {display_name}: {probability:.2%}")
                except Exception as e:
                    print(f"✗ Error predicting with {display_name}: {e}")
                    probability = 0.0
                    risk_label = "Lỗi"
                    status = "❌ Lỗi"
                    is_trained = False
            else:
                # Demo model - show placeholder
                probability = 0.0064  # Demo value 0.64%
                risk_label = "Nguy cơ thấp"
                status = "🔸 DEMO"
            
            results.append({
                'model': display_name,
                'probability': probability,
                'risk_label': risk_label,
                'status': status,
                'is_trained': is_trained
            })
        
        # Sort by probability descending
        results.sort(key=lambda x: x['probability'], reverse=True)
        
        # Display in table
        for i, result in enumerate(results):
            # Model name with DEMO label
            model_display = result['model']
            if not result['is_trained']:
                model_display += " (DEMO)"
            
            self.table.setItem(i, 0, QTableWidgetItem(model_display))
            self.table.setItem(i, 1, QTableWidgetItem(f"{result['probability']:.2%}"))
            self.table.setItem(i, 2, QTableWidgetItem(result['risk_label']))
            self.table.setItem(i, 3, QTableWidgetItem(result['status']))
            
            # Color coding based on risk
            if result['probability'] >= 0.5:
                color = QColor(255, 200, 200)  # Red for high risk
            else:
                color = QColor(200, 255, 200)  # Green for low risk
            
            for col in range(4):
                self.table.item(i, col).setBackground(color)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    # Test data
    test_data = {
        'LIMIT_BAL': 50000,
        'SEX': 1,
        'EDUCATION': 2,
        'MARRIAGE': 1,
        'AGE': 30,
        'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0, 'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
        'PAY_7': 0, 'PAY_8': 0, 'PAY_9': 0, 'PAY_10': 0, 'PAY_11': 0, 'PAY_12': 0,
        'BILL_AMT1': 1000, 'BILL_AMT2': 1000, 'BILL_AMT3': 1000, 'BILL_AMT4': 1000,
        'BILL_AMT5': 1000, 'BILL_AMT6': 1000, 'BILL_AMT7': 1000, 'BILL_AMT8': 1000,
        'BILL_AMT9': 1000, 'BILL_AMT10': 1000, 'BILL_AMT11': 1000, 'BILL_AMT12': 1000,
        'PAY_AMT1': 1000, 'PAY_AMT2': 1000, 'PAY_AMT3': 1000, 'PAY_AMT4': 1000,
        'PAY_AMT5': 1000, 'PAY_AMT6': 1000, 'PAY_AMT7': 1000, 'PAY_AMT8': 1000,
        'PAY_AMT9': 1000, 'PAY_AMT10': 1000, 'PAY_AMT11': 1000, 'PAY_AMT12': 1000
    }
    
    app = QApplication(sys.argv)
    dialog = ModelComparisonDialog(test_data)
    dialog.exec()
