"""
LoginWindowEx
Extended LoginWindow với logic đăng nhập
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSignal

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ui.LoginWindow import Ui_LoginWindow
from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
from services.auth_service import AuthService
from models.user import User


class LoginWindowEx(QMainWindow):
    """
    Extended LoginWindow với logic xử lý đăng nhập
    Emit signal khi login thành công
    """
    
    # Signal emit khi đăng nhập thành công
    login_successful = pyqtSignal(User)
    
    def __init__(self):
        """Khởi tạo LoginWindow"""
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        
        # Connect signals
        self.ui.btnLogin.clicked.connect(self.handle_login)
        self.ui.txtPassword.returnPressed.connect(self.handle_login)
        
        # Init services
        self.db_config = DatabaseConfig.default()
        self.db_connector = None
        self.auth_service = None
    
    def handle_login(self):
        """
        Xử lý sự kiện click nút Login
        """
        username = self.ui.txtUsername.text().strip()
        password = self.ui.txtPassword.text()
        
        # Validate input
        if not username or not password:
            self.ui.lblStatus.setText("⚠ Vui lòng nhập đầy đủ thông tin")
            return
        
        # Connect to database
        if not self.connect_database():
            return
        
        # Attempt login
        try:
            user = self.auth_service.login(username, password)
            
            if user:
                # Login successful
                self.ui.lblStatus.setText("✓ Đăng nhập thành công!")
                self.ui.lblStatus.setStyleSheet("color: green; font-size: 12px;")
                
                # Emit signal
                self.login_successful.emit(user)
                
            else:
                # Login failed
                self.ui.lblStatus.setText("✗ Tên đăng nhập hoặc mật khẩu không đúng")
                self.ui.lblStatus.setStyleSheet("color: red; font-size: 12px;")
        
        except Exception as e:
            self.ui.lblStatus.setText(f"✗ Lỗi: {str(e)}")
            print(f"Login error: {e}")
    
    def connect_database(self) -> bool:
        """
        Kết nối tới database
        
        Returns:
            True nếu kết nối thành công
        """
        if self.db_connector and self.db_connector.connection:
            return True
        
        try:
            self.db_connector = DatabaseConnector(self.db_config)
            success = self.db_connector.connect()
            
            if success:
                self.auth_service = AuthService(self.db_connector)
                return True
            else:
                self.ui.lblStatus.setText("✗ Không thể kết nối database")
                return False
        
        except Exception as e:
            self.ui.lblStatus.setText(f"✗ Lỗi kết nối: {str(e)}")
            print(f"Database connection error: {e}")
            return False
    
    def closeEvent(self, event):
        """Override closeEvent để đóng database connection"""
        if self.db_connector:
            self.db_connector.close()
        event.accept()
