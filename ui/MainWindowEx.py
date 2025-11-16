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
        
        # Tab 1: Dự Báo Rủi Ro
        self.prediction_widget = PredictionTabWidget(self.query_service)
        self.ui.tabWidget.addTab(self.prediction_widget, "📊 Dự Báo Rủi Ro")
        
        # Tab 2: Dashboard
        self.dashboard_widget = DashboardTabWidget()
        self.ui.tabWidget.addTab(self.dashboard_widget, "📈 Dashboard")
    
    def setup_role_permissions(self):
        """
        Thiết lập phân quyền theo role
        
        Rules:
        - Admin: Xem tất cả tabs
        - Technical: Xem Prediction + Dashboard
        - Secretary: Chỉ xem Prediction
        """
        if self.user.role == 'Admin':
            # Admin có quyền tất cả
            print(f"✓ Admin access: All tabs enabled")
        
        elif self.user.role == 'Technical':
            # Technical có quyền Prediction + Dashboard
            print(f"✓ Technical access: Prediction + Dashboard enabled")
        
        elif self.user.role == 'Secretary':
            # Secretary chỉ có quyền Prediction
            # Ẩn tab Dashboard
            dashboard_index = None
            for i in range(self.ui.tabWidget.count()):
                if 'Dashboard' in self.ui.tabWidget.tabText(i):
                    dashboard_index = i
                    break
            
            if dashboard_index is not None:
                self.ui.tabWidget.removeTab(dashboard_index)
            
            print(f"✓ Secretary access: Only Prediction tab enabled")
        
        else:
            # Unknown role - restrict to Prediction only
            print(f"⚠ Unknown role '{self.user.role}': Default to Prediction only")
    
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
