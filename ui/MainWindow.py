"""
MainWindow - Credit Risk System main interface
Features: Prediction, Dashboard, Reports, AI Assistant, Customer Management
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .user_model import User
    from .PredictionTabWidget import PredictionTabWidget
    from .DashboardTabWidget import DashboardTabWidget
    from .ReportTab import ReportTab
    from .AIAssistantWidget import AIAssistantWidget
    from .ModelManagementTab import ModelManagementTab
    from .SystemManagementTab import SystemManagementTab
except Exception:
    from user_model import User
    from PredictionTabWidget import PredictionTabWidget
    from DashboardTabWidget import DashboardTabWidget
    from ReportTab import ReportTab
    from AIAssistantWidget import AIAssistantWidget
    from ModelManagementTab import ModelManagementTab
    from SystemManagementTab import SystemManagementTab

try:
    from .style import STYLE_QSS
except Exception:
    from style import STYLE_QSS

try:
    from .CustomerEntryTab import CustomerEntryTab
except Exception:
    from CustomerEntryTab import CustomerEntryTab

class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Credit Risk System - {self.user.username} ({self.user.role})")
        self.tab = QTabWidget()
        self.setCentralWidget(self.tab)
        self.setStyleSheet(STYLE_QSS)
        self.setup_menu()
        self.setup_tabs()
    
    def setup_menu(self):
        """Thiết lập menu bar với nút đăng xuất"""
        menubar = self.menuBar()
        
        # Menu Tài khoản
        account_menu = menubar.addMenu('⚙️ Tài khoản')
        
        # Action đăng xuất
        logout_action = QAction('🚪 Đăng xuất', self)
        logout_action.setShortcut('Ctrl+Q')
        logout_action.triggered.connect(self.handle_logout)
        account_menu.addAction(logout_action)
    
    def handle_logout(self):
        """Xử lý đăng xuất"""
        reply = QMessageBox.question(
            self,
            'Đăng xuất',
            f'Bạn có chắc muốn đăng xuất khỏi tài khoản "{self.user.username}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print(f"✓ Đăng xuất: {self.user.username}")
            self.logout_signal.emit()
            self.close()

    def setup_tabs(self):
        # Import integration để lấy query_service
        try:
            from .integration import get_db_connector, get_query_service
        except:
            from integration import get_db_connector, get_query_service
        
        db = get_db_connector()
        query_service = get_query_service(db)
        
        self.prediction_tab = PredictionTabWidget(self.user, query_service)
        self.dashboard_tab = DashboardTabWidget(self.user)
        self.report_tab = ReportTab(self.user)
        self.ai_tab = AIAssistantWidget(self.user, db)
        self.customer_tab = CustomerEntryTab(self.user.id)
        self.tab.addTab(self.prediction_tab, '📊 Dự Báo')
        self.tab.addTab(self.dashboard_tab, '📈 Dashboard')
        self.tab.addTab(self.report_tab, '📋 Báo Cáo')
        self.tab.addTab(self.ai_tab, '🤖 AI Trợ Lý')
        self.tab.addTab(self.customer_tab, '👥 Khách Hàng')
        if self.user.is_admin():
            self.ml_tab = ModelManagementTab()
            self.sys_tab = SystemManagementTab()
            self.tab.addTab(self.ml_tab, 'Quản Lý ML')
            self.tab.addTab(self.sys_tab, 'Hệ Thống')
