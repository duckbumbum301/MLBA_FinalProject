"""
MainWindow - Credit Risk System main interface
Features: Prediction, Dashboard, Reports, AI Assistant, Customer Management
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QAction, QPixmap, QIcon
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
        self.build_header_layout()
        self.setStyleSheet(STYLE_QSS)
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

        # Wire navbar buttons to tabs when available
        if hasattr(self, 'btnNavPredict'):
            self.btnNavPredict.clicked.connect(lambda: self.tab.setCurrentWidget(self.prediction_tab))
        if hasattr(self, 'btnNavDashboard'):
            self.btnNavDashboard.clicked.connect(lambda: self.tab.setCurrentWidget(self.dashboard_tab))
        if hasattr(self, 'btnNavReport'):
            self.btnNavReport.clicked.connect(lambda: self.tab.setCurrentWidget(self.report_tab))
        if hasattr(self, 'btnNavCustomers'):
            self.btnNavCustomers.clicked.connect(lambda: self.tab.setCurrentWidget(self.customer_tab))
        if hasattr(self, 'btnNavAI'):
            self.btnNavAI.clicked.connect(lambda: self.tab.setCurrentWidget(self.ai_tab))

    def build_header_layout(self):
        root = QWidget()
        container = QVBoxLayout(root)
        container.setContentsMargins(0,0,0,0)
        container.setSpacing(0)

        # Top blue bar
        topbar = QFrame(); topbar.setObjectName('TopBar')
        tb = QHBoxLayout(topbar); tb.setContentsMargins(16,10,16,10)
        title = QLabel('Credit Risk Management System'); title.setObjectName('Heading2')
        tb.addWidget(title)
        tb.addStretch()
        user_label = QLabel(f"{self.user.username} ({self.user.role})")
        tb.addWidget(user_label)
        btnLogoutTop = QPushButton('Log out'); btnLogoutTop.setObjectName('Secondary')
        btnLogoutTop.clicked.connect(self.handle_logout)
        tb.addWidget(btnLogoutTop)

        # Secondary nav bar
        navbar = QFrame(); navbar.setObjectName('NavBar')
        nb = QHBoxLayout(navbar); nb.setContentsMargins(16,8,16,8)
        logoSmall = QLabel('')
        logo_path = base_dir / 'images' / 'logo.png'
        if logo_path.exists():
            pm2 = QPixmap(str(logo_path))
            logoSmall.setPixmap(pm2.scaledToHeight(22))
        logoSmall.setFixedSize(32, 22)
        nb.addWidget(logoSmall)
        brand = QLabel('NYTDT'); brand.setObjectName('Heading3')
        nb.addWidget(brand)
        self.btnNavPredict = QPushButton('Prediction'); self.btnNavPredict.setObjectName('NavItem')
        self.btnNavDashboard = QPushButton('Dashboard'); self.btnNavDashboard.setObjectName('NavItem')
        self.btnNavReport = QPushButton('Reports'); self.btnNavReport.setObjectName('NavItem')
        self.btnNavCustomers = QPushButton('Customers'); self.btnNavCustomers.setObjectName('NavItem')
        for b in [self.btnNavPredict, self.btnNavDashboard, self.btnNavReport, self.btnNavCustomers]:
            nb.addWidget(b)
        nb.addStretch()
        self.btnNavAI = QPushButton(''); self.btnNavAI.setObjectName('AiButton')
        ai_path = base_dir / 'images' / 'chatbotAI.png'
        if ai_path.exists():
            self.btnNavAI.setIcon(QIcon(str(ai_path)))
            self.btnNavAI.setIconSize(QSize(24,24))
        self.btnNavAI.setFixedSize(36,36)
        nb.addWidget(self.btnNavAI)
        search = QLineEdit(); search.setObjectName('SearchBox'); search.setPlaceholderText('Searching...')
        nb.addWidget(search)

        container.addWidget(topbar)
        container.addWidget(navbar)
        container.addWidget(self.tab)
        self.setCentralWidget(root)
