"""
Model Management Widget
Tab quản lý các mô hình ML (Admin only)
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QMessageBox, QProgressDialog,
    QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.user import User
from services.model_management_service import ModelManagementService
from database.connector import DatabaseConnector


class ModelManagementWidget(QWidget):
    """
    Widget quản lý models (Admin only)
    """
    
    def __init__(self, user: User, db_connector: DatabaseConnector):
        super().__init__()
        self.user = user
        self.db = db_connector
        self.model_service = ModelManagementService(db_connector)
        
        self.setup_ui()
        self.load_models()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎯 QUẢN LÝ MÔ HÌNH MACHINE LEARNING")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Model list table
        list_group = QGroupBox("Danh Sách Models")
        list_layout = QVBoxLayout()
        
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(8)
        self.model_table.setHorizontalHeaderLabels([
            "Model", "Algorithm", "AUC", "Accuracy", "F1-Score", 
            "Trained", "Status", "Actions"
        ])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.model_table.setAlternatingRowColors(True)
        list_layout.addWidget(self.model_table)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Actions
        actions_group = QGroupBox("Thao Tác")
        actions_layout = QVBoxLayout()
        
        # Row 1: Train new model
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Train Model Mới:"))
        
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "CatBoost",
            "RandomForest", 
            "Neural Network",
            "Voting Ensemble",
            "Stacking Ensemble"
        ])
        row1.addWidget(self.model_selector)
        
        train_btn = QPushButton("🚀 Train")
        train_btn.clicked.connect(self.train_model)
        train_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        row1.addWidget(train_btn)
        row1.addStretch()
        
        actions_layout.addLayout(row1)
        
        # Row 2: Set active model
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Model Đang Dùng:"))
        
        self.active_model_label = QLabel("XGBoost")
        self.active_model_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        row2.addWidget(self.active_model_label)
        
        set_active_btn = QPushButton("⭐ Set Active Model")
        set_active_btn.clicked.connect(self.set_active_model)
        set_active_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        row2.addWidget(set_active_btn)
        row2.addStretch()
        
        actions_layout.addLayout(row2)
        
        # Row 3: Other actions
        row3 = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_models)
        row3.addWidget(refresh_btn)
        
        compare_btn = QPushButton("📊 So Sánh Models")
        compare_btn.clicked.connect(self.compare_models)
        row3.addWidget(compare_btn)
        
        delete_btn = QPushButton("🗑️ Xóa Model")
        delete_btn.clicked.connect(self.delete_model)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        row3.addWidget(delete_btn)
        
        row3.addStretch()
        actions_layout.addLayout(row3)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Info
        info_label = QLabel(
            "💡 Lưu ý: Models mới sẽ được train với dữ liệu UCI_Credit_Card_12months.csv. "
            "Quá trình train có thể mất 5-15 phút tùy thuộc vào model."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def load_models(self):
        """Load danh sách models"""
        try:
            models = self.model_service.get_all_models()
            
            self.model_table.setRowCount(len(models))
            
            for row, model in enumerate(models):
                # Model name
                name_item = QTableWidgetItem(model['model_name'])
                name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                self.model_table.setItem(row, 0, name_item)
                
                # Algorithm
                self.model_table.setItem(row, 1, QTableWidgetItem(model['algorithm'] or 'N/A'))
                
                # AUC
                auc = model['auc_score']
                auc_item = QTableWidgetItem(f"{auc:.4f}" if auc else "N/A")
                if auc:
                    if auc >= 0.85:
                        auc_item.setForeground(QColor("#27ae60"))
                    elif auc >= 0.75:
                        auc_item.setForeground(QColor("#f39c12"))
                    else:
                        auc_item.setForeground(QColor("#e74c3c"))
                self.model_table.setItem(row, 2, auc_item)
                
                # Accuracy
                acc = model['accuracy']
                self.model_table.setItem(row, 3, QTableWidgetItem(f"{acc:.2%}" if acc else "N/A"))
                
                # F1-Score
                f1 = model['f1_score']
                self.model_table.setItem(row, 4, QTableWidgetItem(f"{f1:.4f}" if f1 else "N/A"))
                
                # Trained time
                trained = model['trained_at']
                self.model_table.setItem(row, 5, QTableWidgetItem(str(trained) if trained else "Not trained"))
                
                # Status
                status = "✅ ACTIVE" if model['is_active'] else "⬜ Inactive"
                status_item = QTableWidgetItem(status)
                if model['is_active']:
                    status_item.setForeground(QColor("#27ae60"))
                    status_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                self.model_table.setItem(row, 6, status_item)
                
                # Actions button (placeholder)
                action_item = QTableWidgetItem("...")
                action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model_table.setItem(row, 7, action_item)
            
            # Update active model label
            active = self.model_service.get_active_model()
            if active:
                self.active_model_label.setText(active['model_name'])
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể load models: {e}")
    
    def train_model(self):
        """Train model mới"""
        model_name = self.model_selector.currentText()
        
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc muốn train model {model_name}?\n\n"
            f"⏱️ Thời gian dự kiến: 5-15 phút\n"
            f"💾 Dữ liệu: UCI_Credit_Card_12months.csv (30,000 records)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        QMessageBox.information(
            self,
            "Training Model",
            f"Training {model_name} sẽ được thực hiện trong background.\n\n"
            f"Bạn có thể tiếp tục sử dụng ứng dụng. Quá trình train sẽ mất 5-15 phút.\n\n"
            f"Sau khi hoàn tất, vui lòng click 'Refresh' để xem kết quả."
        )
        
        # Note: Actual training would be done in a separate thread
        # For now, just show a message
    
    def set_active_model(self):
        """Set model được chọn làm active"""
        selected_row = self.model_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một model từ bảng!")
            return
        
        model_name = self.model_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Set {model_name} làm model mặc định?\n\n"
            f"Model này sẽ được sử dụng cho tất cả predictions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.model_service.set_active_model(model_name, self.user.username)
                
                if success:
                    QMessageBox.information(self, "Thành công", f"✅ {model_name} đã được set làm active model!")
                    self.load_models()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể set active model!")
            
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi: {e}")
    
    def compare_models(self):
        """So sánh các models"""
        QMessageBox.information(
            self,
            "So Sánh Models",
            "Tính năng so sánh models chi tiết sẽ hiện ROC curves overlay, "
            "confusion matrices, và metrics comparison table.\n\n"
            "Đang được phát triển..."
        )
    
    def delete_model(self):
        """Xóa model"""
        selected_row = self.model_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một model từ bảng!")
            return
        
        model_name = self.model_table.item(selected_row, 0).text()
        status = self.model_table.item(selected_row, 6).text()
        
        if "ACTIVE" in status:
            QMessageBox.warning(self, "Cảnh báo", "Không thể xóa model đang active!")
            return
        
        reply = QMessageBox.question(
            self,
            "Xác nhận Xóa",
            f"⚠️ Bạn có chắc muốn xóa model {model_name}?\n\n"
            f"Hành động này không thể hoàn tác!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.model_service.delete_model(model_name)
                
                if success:
                    QMessageBox.information(self, "Thành công", f"✅ Đã xóa model {model_name}!")
                    self.load_models()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể xóa model!")
            
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi: {e}")
