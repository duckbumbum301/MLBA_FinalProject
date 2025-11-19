"""
MainWindow - Credit Risk System main interface
Features: Prediction, Dashboard, Reports, AI Assistant, Customer Management
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QLineEdit, QDialog
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

# Customers tab removed per requirement

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
        self.dashboard_tab = DashboardTabWidget(self.user, query_service)
        self.report_tab = ReportTab(self.user)
        self._db_for_ai = db
        self.tab.addTab(self.prediction_tab, '📊 Dự Báo')
        self.tab.addTab(self.dashboard_tab, '📈 Dashboard')
        self.tab.addTab(self.report_tab, '📋 Báo Cáo')
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
        if hasattr(self, 'btnNavML') and hasattr(self, 'ml_tab'):
            self.btnNavML.clicked.connect(lambda: self.tab.setCurrentWidget(self.ml_tab))
        if hasattr(self, 'btnNavSys') and hasattr(self, 'sys_tab'):
            self.btnNavSys.clicked.connect(lambda: self.tab.setCurrentWidget(self.sys_tab))
        if hasattr(self, 'btnNavAI'):
            self.btnNavAI.clicked.connect(self.open_ai_popup)
        
        # Reflect active state in navbar
        self.tab.currentChanged.connect(self.on_tab_changed)
        # Set initial active
        try:
            current_idx = self.tab.currentIndex()
            self.on_tab_changed(current_idx)
        except Exception:
            pass

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
        nb = QHBoxLayout(navbar); nb.setContentsMargins(16,8,16,8); nb.setSpacing(8)
        logoSmall = QLabel('')
        logo_path = base_dir / 'images' / 'logo.png'
        if logo_path.exists():
            pm2 = QPixmap(str(logo_path))
            logoSmall.setPixmap(pm2.scaledToHeight(32))
        logoSmall.setFixedSize(48, 32)
        nb.addWidget(logoSmall)
        brand = QLabel('NYTDT'); brand.setObjectName('Heading3')
        nb.addWidget(brand)
        nb.addSpacing(80)
        self.btnNavPredict = QPushButton('Prediction'); self.btnNavPredict.setObjectName('NavItem'); self.btnNavPredict.setCheckable(True)
        self.btnNavDashboard = QPushButton('Dashboard'); self.btnNavDashboard.setObjectName('NavItem'); self.btnNavDashboard.setCheckable(True)
        self.btnNavReport = QPushButton('Reports'); self.btnNavReport.setObjectName('NavItem'); self.btnNavReport.setCheckable(True)
        if self.user.is_admin():
            self.btnNavML = QPushButton('Quản Lý ML'); self.btnNavML.setObjectName('NavItem'); self.btnNavML.setCheckable(True)
            self.btnNavSys = QPushButton('Hệ Thống'); self.btnNavSys.setObjectName('NavItem'); self.btnNavSys.setCheckable(True)
            nav_buttons = [self.btnNavPredict, self.btnNavDashboard, self.btnNavReport, self.btnNavML, self.btnNavSys]
        else:
            nav_buttons = [self.btnNavPredict, self.btnNavDashboard, self.btnNavReport]
        for b in nav_buttons:
            nb.addWidget(b)
        nb.addStretch()
        self.btnNavAI = QPushButton(''); self.btnNavAI.setObjectName('AiButton')
        ai_path = base_dir / 'images' / 'chatbotAI.png'
        if ai_path.exists():
            self.btnNavAI.setIcon(QIcon(str(ai_path)))
            self.btnNavAI.setIconSize(QSize(32,32))
        self.btnNavAI.setFixedSize(44,44)
        nb.addWidget(self.btnNavAI)
        search = QLineEdit(); search.setObjectName('SearchBox'); search.setPlaceholderText('Searching...')
        nb.addWidget(search)

        container.addWidget(topbar)
        container.addWidget(navbar)
        container.addWidget(self.tab)
        
        footer = QFrame(); footer.setObjectName('Footer')
        fl = QHBoxLayout(footer); fl.setContentsMargins(16,8,16,8)
        fl.addStretch()
        txtLeft = QLabel('© Copyright 205 | Bản quyền thuộc sở hữu của')
        brand = QLabel(' NYTDT')
        brand.setObjectName('FooterBrand')
        fl.addWidget(txtLeft)
        fl.addWidget(brand)
        fl.addStretch()
        container.addWidget(footer)
        self.setCentralWidget(root)

    def open_ai_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('AI Copilot')
        lay = QVBoxLayout(dlg)
        aiw = AIAssistantWidget(self.user, self._db_for_ai)
        lay.addWidget(aiw)
        dlg.resize(900, 600)
        dlg.exec()

    def on_tab_changed(self, idx: int):
        w = self.tab.widget(idx)
        def set_active(btn, active):
            btn.setChecked(active)
        set_active(self.btnNavPredict, w is getattr(self, 'prediction_tab', None))
        set_active(self.btnNavDashboard, w is getattr(self, 'dashboard_tab', None))
        set_active(self.btnNavReport, w is getattr(self, 'report_tab', None))
        if hasattr(self, 'btnNavML'):
            set_active(self.btnNavML, w is getattr(self, 'ml_tab', None))
        if hasattr(self, 'btnNavSys'):
            set_active(self.btnNavSys, w is getattr(self, 'sys_tab', None))
