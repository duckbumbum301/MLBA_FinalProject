"""
MainWindowEx
Extended MainWindow với logic quản lý tabs và phân quyền
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ui.MainWindow import Ui_MainWindow
from ui.PredictionTabWidget import PredictionTabWidget
from ui.DashboardTabWidget import DashboardTabWidget
from ui.AIAssistantWidget import AIAssistantWidget
from ui.ModelManagementWidget import ModelManagementWidget
from ui.SystemManagementWidget import SystemManagementWidget
from models.user import User
from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
from services.query_service import QueryService


class MainWindowEx(QMainWindow):
    """
    Extended MainWindow với logic chính
    - Quản lý tabs
    - Phân quyền theo role
    - Xử lý logout
    """
    
    # Signal emit khi logout
    logout_signal = pyqtSignal()
    
    def __init__(self, user: User):
        """
        Khởi tạo MainWindow
        
        Args:
            user: User đã đăng nhập
        """
        super().__init__()
        self.user = user
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Init database connection
        self.db_config = DatabaseConfig.default()
        self.db_connector = DatabaseConnector(self.db_config)
        self.db_connector.connect()
        
        # Init services
        self.query_service = QueryService(self.db_connector)
        
        # Setup UI
        self.setup_user_info()
        self.setup_tabs()
        self.setup_role_permissions()
        
        # Connect signals
        self.ui.btnLogout.clicked.connect(self.handle_logout)
    
    def setup_user_info(self):
        """Hiển thị thông tin user"""
        self.ui.lblWelcome.setText(f"Xin chào, {self.user.username} ({self.user.role})")
    
    def setup_tabs(self):
        """Thiết lập nội dung các tabs"""
        # Clear default tabs
        self.ui.tabWidget.clear()
        
        # Tab 1: Dự Báo Rủi Ro (All users)
        self.prediction_widget = PredictionTabWidget(self.user, self.query_service)
        self.ui.tabWidget.addTab(self.prediction_widget, "📊 Dự Báo Rủi Ro")
        
        # Tab 2: Dashboard (All users - limited for User role)
        self.dashboard_widget = DashboardTabWidget()
        self.ui.tabWidget.addTab(self.dashboard_widget, "📈 Dashboard")
        
        # Tab 3: AI Trợ Lý (All users)
        try:
            self.ai_assistant_widget = AIAssistantWidget(self.user, self.db_connector)
            self.ui.tabWidget.addTab(self.ai_assistant_widget, "🤖 AI Trợ Lý")
        except Exception as e:
            print(f"⚠ Could not load AI Assistant: {e}")
        
        # Tab 4 & 5: Admin only
        if self.user.is_admin():
            # Tab 4: Quản Lý Models (Admin only)
            try:
                self.model_management_widget = ModelManagementWidget(self.user, self.db_connector)
                self.ui.tabWidget.addTab(self.model_management_widget, "🎯 Quản Lý ML")
            except Exception as e:
                print(f"⚠ Could not load Model Management: {e}")
            
            # Tab 5: Quản Lý Hệ Thống (Admin only)
            try:
                self.system_widget = SystemManagementWidget(self.user, self.db_connector)
                self.ui.tabWidget.addTab(self.system_widget, "⚙️ Hệ Thống")
            except Exception as e:
                print(f"⚠ Could not load System Management: {e}")
    
    def setup_role_permissions(self):
        """
        Thiết lập phân quyền theo role
        - User: Thấy 3 tabs (Dự Báo, Dashboard, AI Trợ Lý)
        - Admin: Thấy 5 tabs (thêm Quản Lý ML, Hệ Thống)
        """
        if self.user.is_admin():
            # Admin: Full access to all 5 tabs
            self.setWindowTitle(f"Credit Risk System - Admin: {self.user.username}")
            print(f"✓ Admin access: 5 tabs enabled")
        else:
            # User: Limited access to 3 tabs only
            self.setWindowTitle(f"Credit Risk System - User: {self.user.username}")
            print(f"✓ User access: 3 tabs enabled")
    
    def handle_logout(self):
        """Xử lý sự kiện logout"""
        print(f"Đăng xuất user: {self.user.username}")
        
        # Close database connection
        if self.db_connector:
            self.db_connector.close()
        
        # Hide window
        self.hide()
        
        # Emit signal
        self.logout_signal.emit()
    
    def closeEvent(self, event):
        """Override closeEvent"""
        if self.db_connector:
            self.db_connector.close()
        event.accept()

