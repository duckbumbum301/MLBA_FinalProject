"""
AI Assistant Widget  
Tab chat với Gemini AI
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.user import User
from services.gemini_service import GeminiService
from database.connector import DatabaseConnector


class AIAssistantWidget(QWidget):
    """
    Widget cho Tab AI Trợ Lý
    Chat interface với Gemini AI
    """
    
    def __init__(self, user: User, db_connector: DatabaseConnector):
        super().__init__()
        self.user = user
        self.db = db_connector
        
        # Initialize Gemini Service
        try:
            self.gemini_service = GeminiService(db_connector, user.id)
            self.gemini_available = self.gemini_service.is_available()
        except Exception as e:
            print(f"⚠ Gemini Service initialization failed: {e}")
            self.gemini_service = None
            self.gemini_available = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🤖 AI TRỢ LÝ - GEMINI")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status indicator
        if self.gemini_available:
            status = QLabel("✅ AI Assistant đã sẵn sàng")
            status.setStyleSheet("color: green; font-weight: bold;")
        else:
            status = QLabel("⚠️ AI Assistant chưa cấu hình. Vui lòng thêm API key vào config/gemini_config.py")
            status.setStyleSheet("color: orange; font-weight: bold;")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)
        
        # Context selector
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("Ngữ cảnh:"))
        
        self.context_selector = QComboBox()
        self.context_selector.addItems([
            "Hỏi chung về Credit Risk",
            "Giải thích dự báo vừa rồi",
            "So sánh các models",
            "Tư vấn chiến lược"
        ])
        context_layout.addWidget(self.context_selector)
        context_layout.addStretch()
        layout.addLayout(context_layout)
        
        # Chat history area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nhập câu hỏi của bạn...")
        self.input_field.setFont(QFont("Segoe UI", 10))
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Gửi")
        self.send_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("Câu hỏi nhanh:"))
        
        quick_btn1 = QPushButton("Credit risk là gì?")
        quick_btn1.clicked.connect(lambda: self.quick_ask("Giải thích credit risk scoring là gì?"))
        quick_layout.addWidget(quick_btn1)
        
        quick_btn2 = QPushButton("Top 3 yếu tố rủi ro")
        quick_btn2.clicked.connect(lambda: self.quick_ask("3 yếu tố quan trọng nhất trong credit risk?"))
        quick_layout.addWidget(quick_btn2)
        
        quick_btn3 = QPushButton("Cách giảm rủi ro")
        quick_btn3.clicked.connect(lambda: self.quick_ask("Đề xuất 5 cách giảm rủi ro tín dụng"))
        quick_layout.addWidget(quick_btn3)
        
        if self.user.is_admin():
            quick_btn4 = QPushButton("So sánh models")
            quick_btn4.clicked.connect(lambda: self.quick_ask("So sánh ưu nhược điểm XGBoost, LightGBM, CatBoost"))
            quick_layout.addWidget(quick_btn4)
        
        quick_layout.addStretch()
        layout.addLayout(quick_layout)
        
        # Clear button
        clear_btn = QPushButton("Xóa lịch sử chat")
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        # Load chat history
        self.load_chat_history()
        
        # Disable if not available
        if not self.gemini_available:
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
    
    def send_message(self):
        """Gửi message tới Gemini"""
        message = self.input_field.text().strip()
        
        if not message:
            return
        
        if not self.gemini_available:
            QMessageBox.warning(
                self,
                "AI Không Khả Dụng",
                "Vui lòng cấu hình Gemini API key trong config/gemini_config.py"
            )
            return
        
        # Disable input
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.send_button.setText("Đang xử lý...")
        
        # Display user message
        self.append_message("👤 Bạn", message, "#3498db")
        
        # Clear input
        self.input_field.clear()
        
        try:
            # Send to Gemini
            response = self.gemini_service.send_message(
                message=message,
                context_type=self.context_selector.currentText()
            )
            
            # Display AI response
            self.append_message("🤖 AI", response, "#27ae60")
        
        except Exception as e:
            error_msg = f"❌ Lỗi: {str(e)}"
            self.append_message("⚠️ Hệ thống", error_msg, "#e74c3c")
        
        finally:
            # Re-enable input
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            self.send_button.setText("Gửi")
            self.input_field.setFocus()
    
    def quick_ask(self, question: str):
        """Gửi câu hỏi nhanh"""
        self.input_field.setText(question)
        self.send_message()
    
    def append_message(self, sender: str, message: str, color: str):
        """Thêm message vào chat display"""
        html = f"""
        <div style='margin-bottom: 15px;'>
            <b style='color: {color}; font-size: 12px;'>{sender}:</b><br>
            <div style='padding: 10px; background-color: white; border-left: 3px solid {color}; 
                        border-radius: 5px; margin-top: 5px;'>
                {message.replace(chr(10), '<br>')}
            </div>
        </div>
        """
        self.chat_display.append(html)
        
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def load_chat_history(self):
        """Load lịch sử chat từ database"""
        if not self.gemini_available or not self.gemini_service:
            return
        
        try:
            history = self.gemini_service.get_chat_history(limit=10)
            
            if history:
                self.append_message("📜 Hệ thống", "Lịch sử chat gần đây:", "#95a5a6")
                
                for item in history[-5:]:  # Show last 5
                    self.append_message("👤 Bạn", item['user_message'], "#3498db")
                    self.append_message("🤖 AI", item['ai_response'], "#27ae60")
        except:
            pass
    
    def clear_chat(self):
        """Xóa lịch sử chat"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa toàn bộ lịch sử chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            if self.gemini_service:
                self.gemini_service.clear_chat_history()
            self.append_message("✅ Hệ thống", "Lịch sử chat đã được xóa", "#27ae60")
