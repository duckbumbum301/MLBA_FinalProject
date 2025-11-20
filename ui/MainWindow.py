"""
MainWindow - Credit Risk System main interface
Features: Prediction, Dashboard, Reports, AI Assistant, Customer Management
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QLineEdit, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import pyqtSignal, QSize, QTimer, Qt
from PyQt6.QtGui import QAction, QPixmap, QIcon
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .user_model import User
    from .PredictionTabNew import PredictionTabWidget
    from .DashboardTabWidget import DashboardTabWidget
    from .ReportTab import ReportTab
    from .UserReportTab import UserReportTab
    from .AIAssistantWidget import AIAssistantWidget
    from .SystemManagementTab import SystemManagementTab
except Exception:
    from user_model import User
    from PredictionTabNew import PredictionTabWidget
    from DashboardTabWidget import DashboardTabWidget
    from ReportTab import ReportTab
    from UserReportTab import UserReportTab
    from AIAssistantWidget import AIAssistantWidget
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
        try:
            self.tab.setTabBarAutoHide(True)
        except Exception:
            pass
        try:
            self.tab.tabBar().hide()
        except Exception:
            pass
    
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
        self.report_tab = ReportTab(self.user) if self.user.is_admin() else UserReportTab(self.user)
        self._db_for_ai = db
        self.tab.addTab(self.prediction_tab, '📊 Dự Báo')
        self.tab.addTab(self.dashboard_tab, '📈 Bảng Điều Khiển')
        self.tab.addTab(self.report_tab, '📋 Báo Cáo')
        if self.user.is_admin():
            self.sys_tab = SystemManagementTab()
            self.tab.addTab(self.sys_tab, 'Hệ Thống')

        # Wire navbar buttons to tabs when available
        if hasattr(self, 'btnNavPredict'):
            self.btnNavPredict.clicked.connect(lambda: self.tab.setCurrentWidget(self.prediction_tab))
        if hasattr(self, 'btnNavDashboard'):
            self.btnNavDashboard.clicked.connect(lambda: self.tab.setCurrentWidget(self.dashboard_tab))
        if hasattr(self, 'btnNavReport'):
            self.btnNavReport.clicked.connect(lambda: self.tab.setCurrentWidget(self.report_tab))
        try:
            self.prediction_tab.prediction_logged.connect(self.dashboard_tab.refresh_dashboard)
        except Exception:
            pass
        if hasattr(self, 'btnNavSys') and hasattr(self, 'sys_tab'):
            self.btnNavSys.clicked.connect(lambda: self.tab.setCurrentWidget(self.sys_tab))
        
        # Reflect active state in navbar
        self.tab.currentChanged.connect(self.on_tab_changed)
        # Set initial active
        try:
            current_idx = self.tab.currentIndex()
            self.on_tab_changed(current_idx)
        except Exception:
            pass
        try:
            self.update_notify_badge()
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
        title = QLabel('Hệ Thống Quản Lý Rủi Ro Tín Dụng'); title.setObjectName('Heading2')
        tb.addWidget(title)
        tb.addStretch()
        user_label = QLabel(f"{self.user.username} ({self.user.role})")
        tb.addWidget(user_label)
        btnLogoutTop = QPushButton('Đăng xuất'); btnLogoutTop.setObjectName('Secondary')
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
        self.btnNavPredict = QPushButton('Dự Báo'); self.btnNavPredict.setObjectName('NavItem'); self.btnNavPredict.setCheckable(True)
        self.btnNavDashboard = QPushButton('Bảng Điều Khiển'); self.btnNavDashboard.setObjectName('NavItem'); self.btnNavDashboard.setCheckable(True)
        self.btnNavReport = QPushButton('Báo Cáo'); self.btnNavReport.setObjectName('NavItem'); self.btnNavReport.setCheckable(True)
        if self.user.is_admin():
            self.btnNavSys = QPushButton('Hệ Thống'); self.btnNavSys.setObjectName('NavItem'); self.btnNavSys.setCheckable(True)
            nav_buttons = [self.btnNavPredict, self.btnNavDashboard, self.btnNavReport, self.btnNavSys]
        else:
            nav_buttons = [self.btnNavPredict, self.btnNavDashboard, self.btnNavReport]
        for b in nav_buttons:
            nb.addWidget(b)
        nb.addStretch()
        self.btnNotify = QPushButton('🔔'); self.btnNotify.setObjectName('NotifyButton'); self.btnNotify.setCheckable(False)
        self.btnNotify.setFixedSize(34,34)
        self.btnNotify.clicked.connect(self.open_support_requests_popup)
        self.btnNotify.setVisible(self.user.is_admin())
        nb.addWidget(self.btnNotify)
        search = QLineEdit(); search.setObjectName('SearchBox'); search.setPlaceholderText('Tìm kiếm...')
        nb.addWidget(search)
        self.lblNotifyBadge = QLabel(''); self.lblNotifyBadge.setObjectName('NotifyBadge'); self.lblNotifyBadge.setParent(self.btnNotify)
        self.lblNotifyBadge.setFixedSize(18,18)
        try:
            self.lblNotifyBadge.move(self.btnNotify.width()-14, 0)
        except Exception:
            pass

        container.addWidget(topbar)
        container.addWidget(navbar)
        container.addWidget(self.tab)
        
        footer = QFrame(); footer.setObjectName('Footer')
        fl = QHBoxLayout(footer); fl.setContentsMargins(16,8,16,8)
        fl.addStretch()
        txtLeft = QLabel('© Bản quyền 205 | Thuộc sở hữu của')
        brand = QLabel(' NYTDT')
        brand.setObjectName('FooterBrand')
        fl.addWidget(txtLeft)
        fl.addWidget(brand)
        fl.addStretch()
        container.addWidget(footer)
        self.setCentralWidget(root)
        try:
            self.chatFab = QPushButton('', self)
            self.chatFab.setObjectName('ChatFab')
            ai_path = base_dir / 'images' / 'chatbotAI.png'
            if ai_path.exists():
                self.chatFab.setIcon(QIcon(str(ai_path)))
                self.chatFab.setIconSize(QSize(28,28))
            self.chatFab.setFixedSize(56,56)
            self.chatFab.setStyleSheet("background-color:#AFDDFF; border-radius:28px; color:#ffffff;")
            self.chatFab.clicked.connect(self.open_ai_popup)
            self.chatFab.raise_()
            self._chatFabBottomOffset = 120
            # Initial position
            try:
                m = 16
                x = self.width() - m - self.chatFab.width()
                y = self.height() - (m + self._chatFabBottomOffset) - self.chatFab.height()
                self.chatFab.move(int(x), int(y))
            except Exception:
                pass
        except Exception:
            pass

        try:
            self._notifyTimer = QTimer(self)
            self._notifyTimer.setInterval(5000)
            self._notifyTimer.timeout.connect(self.update_notify_badge)
            self._notifyTimer.start()
            self.update_notify_badge()
        except Exception:
            pass

    def open_ai_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Trợ lý AI')
        try:
            icon_path = base_dir / 'images' / 'logo.png'
            if icon_path.exists():
                dlg.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
        lay = QVBoxLayout(dlg)
        aiw = AIAssistantWidget(self.user, self._db_for_ai)
        lay.addWidget(aiw)
        dlg.resize(900, 600)
        dlg.exec()

    def update_notify_badge(self):
        try:
            proj = Path(__file__).resolve().parents[1]
            cnt = 0
            import json
            f1 = proj / 'outputs' / 'system' / 'forgot_requests.json'
            if f1.exists():
                try:
                    items = json.loads(f1.read_text(encoding='utf-8'))
                    cnt += len([i for i in items if str(i.get('status','')) == 'pending'])
                except Exception:
                    pass
            f2 = proj / 'outputs' / 'system' / 'signup_requests.json'
            if f2.exists():
                try:
                    items2 = json.loads(f2.read_text(encoding='utf-8'))
                    cnt += len([i for i in items2 if str(i.get('status','')) == 'pending'])
                except Exception:
                    pass
            self.lblNotifyBadge.setText(str(cnt))
            self.lblNotifyBadge.setVisible(cnt > 0 and self.user.is_admin())
            self.btnNotify.setVisible(self.user.is_admin())
        except Exception:
            try:
                self.lblNotifyBadge.setVisible(False)
            except Exception:
                pass

    def open_support_requests_popup(self):
        try:
            if not self.user.is_admin():
                return
        except Exception:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle('Yêu cầu hỗ trợ')
        dlg.setFixedSize(780, 420)
        try:
            icon_path = base_dir / 'images' / 'logo.png'
            if icon_path.exists():
                dlg.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
        try:
            dlg.setSizeGripEnabled(False)
        except Exception:
            pass
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
        title = QLabel('Yêu cầu hỗ trợ'); title.setObjectName('SectionTitle'); title.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(title)
        table = QTableWidget(0,4); table.setHorizontalHeaderLabels(['Họ tên','Email','User','Thời điểm'])
        try:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        # Signup requests section
        title2 = QLabel('Yêu cầu đăng ký tài khoản'); title2.setObjectName('SectionTitle'); title2.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(title2)
        table2 = QTableWidget(0,3); table2.setHorizontalHeaderLabels(['Username','Role','Thời điểm'])
        try:
            table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        btns = QHBoxLayout(); btnRefresh = QPushButton('Làm mới'); btnResolve = QPushButton('Đánh dấu đã xử lý'); btnResolve2 = QPushButton('Duyệt đăng ký')
        btns.addWidget(btnRefresh); btns.addWidget(btnResolve); btns.addWidget(btnResolve2)
        lay.addWidget(table)
        lay.addWidget(table2)
        lay.addLayout(btns)
        def load_items():
            try:
                proj = Path(__file__).resolve().parents[1]
                import json
                f = proj / 'outputs' / 'system' / 'forgot_requests.json'
                items = []
                if f.exists():
                    items = json.loads(f.read_text(encoding='utf-8'))
                pending = [i for i in items if str(i.get('status','')) == 'pending']
                table.setRowCount(len(pending))
                for i, r in enumerate(pending):
                    table.setItem(i,0,QTableWidgetItem(str(r.get('full_name',''))))
                    table.setItem(i,1,QTableWidgetItem(str(r.get('email',''))))
                    table.setItem(i,2,QTableWidgetItem(str(r.get('username',''))))
                    table.setItem(i,3,QTableWidgetItem(str(r.get('ts',''))))
                f2 = proj / 'outputs' / 'system' / 'signup_requests.json'
                items2 = []
                if f2.exists():
                    items2 = json.loads(f2.read_text(encoding='utf-8'))
                pending2 = [i for i in items2 if str(i.get('status','')) == 'pending']
                table2.setRowCount(len(pending2))
                for i, r in enumerate(pending2):
                    table2.setItem(i,0,QTableWidgetItem(str(r.get('username',''))))
                    table2.setItem(i,1,QTableWidgetItem(str(r.get('role',''))))
                    table2.setItem(i,2,QTableWidgetItem(str(r.get('ts',''))))
            except Exception:
                table.setRowCount(0)
                table2.setRowCount(0)
        def mark_resolved():
            try:
                row = table.currentRow()
                if row < 0:
                    return
                email = table.item(row,1).text() if table.item(row,1) else ''
                name = table.item(row,0).text() if table.item(row,0) else ''
                proj = Path(__file__).resolve().parents[1]
                f = proj / 'outputs' / 'system' / 'forgot_requests.json'
                if not f.exists():
                    return
                import json
                items = json.loads(f.read_text(encoding='utf-8'))
                for i in items:
                    if str(i.get('email','')) == email and str(i.get('full_name','')) == name and str(i.get('status','')) == 'pending':
                        i['status'] = 'resolved'
                        break
                f.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
                load_items()
                self.update_notify_badge()
            except Exception:
                pass
        def approve_signup():
            try:
                row = table2.currentRow()
                if row < 0:
                    return
                username = table2.item(row,0).text() if table2.item(row,0) else ''
                proj = Path(__file__).resolve().parents[1]
                f2 = proj / 'outputs' / 'system' / 'signup_requests.json'
                if not f2.exists():
                    return
                import json
                items2 = json.loads(f2.read_text(encoding='utf-8'))
                # Find request and create actual user
                found = None
                for i in items2:
                    if str(i.get('username','')) == username and str(i.get('status','')) == 'pending':
                        found = i
                        break
                if found is None:
                    return
                # Create DB user
                try:
                    from services.integration import get_db_connector
                except Exception:
                    from integration import get_db_connector
                from services.auth_service import AuthService
                db = get_db_connector()
                auth = AuthService(db)
                ok = auth.create_user(found.get('username',''), found.get('password','123'), found.get('role','User'))
                db.close()
                if ok:
                    found['status'] = 'resolved'
                f2.write_text(json.dumps(items2, ensure_ascii=False, indent=2), encoding='utf-8')
                load_items()
                self.update_notify_badge()
            except Exception:
                pass
        btnRefresh.clicked.connect(load_items)
        btnResolve.clicked.connect(mark_resolved)
        btnResolve2.clicked.connect(approve_signup)
        load_items()
        dlg.exec()

    def on_tab_changed(self, idx: int):
        w = self.tab.widget(idx)
        def set_active(btn, active):
            btn.setChecked(active)
        set_active(self.btnNavPredict, w is getattr(self, 'prediction_tab', None))
        set_active(self.btnNavDashboard, w is getattr(self, 'dashboard_tab', None))
        set_active(self.btnNavReport, w is getattr(self, 'report_tab', None))
        if hasattr(self, 'btnNavSys'):
            set_active(self.btnNavSys, w is getattr(self, 'sys_tab', None))

    def resizeEvent(self, event):
        try:
            m = 16
            if hasattr(self, 'chatFab') and self.chatFab:
                x = self.width() - m - self.chatFab.width()
                off = getattr(self, '_chatFabBottomOffset', 120)
                y = self.height() - (m + off) - self.chatFab.height()
                self.chatFab.move(int(x), int(y))
        except Exception:
            pass
        return super().resizeEvent(event)
