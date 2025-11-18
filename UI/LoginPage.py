from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from integration import get_db_connector
    from user_model import User as SimpleUser
except Exception:
    from .integration import get_db_connector
    from .user_model import User as SimpleUser

# Import AuthService từ services
try:
    proj = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(proj))
    from services.auth_service import AuthService
except Exception:
    AuthService = None

# Import STYLE_QSS cho UI
try:
    from .style import STYLE_QSS
except Exception:
    from style import STYLE_QSS

class LoginPage(QWidget):
    login_success = pyqtSignal(SimpleUser)
    open_signup = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLE_QSS)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('LoginPage')
        root = QVBoxLayout(); root.setContentsMargins(0,0,0,0)
        top = QFrame(); top.setObjectName('TopBar'); th = QHBoxLayout(top); th.setContentsMargins(16,8,16,8)
        titleBar = QLabel('Credit Risk Management System')
        th.addWidget(titleBar)
        th.addStretch()
        right = QLabel('Not logged in'); right.setObjectName('HeaderStatus'); th.addWidget(right)
        root.addWidget(top)
        center = QVBoxLayout()
        wrapper = QWidget(); wrapper.setObjectName('Card'); wrapper.setMaximumWidth(520)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0,0,0,40))
        wrapper.setGraphicsEffect(shadow)
        card = QVBoxLayout(wrapper); card.setContentsMargins(20,20,20,20)
        title = QLabel('Welcome to NYTDT - Credit Risk Management System!')
        title.setObjectName('CardTitle')
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        logo = QLabel()
        logo.setObjectName('Logo')
        pix = QPixmap(str(base_dir / 'images' / 'logo_nytdt.png'))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        form = QVBoxLayout(); form.setSpacing(10)
        self.txtUsername = QLineEdit(); self.txtUsername.setPlaceholderText('Enter your user name')
        self.txtUsername.setText('babyshark')
        self.txtPassword = QLineEdit(); self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password); self.txtPassword.setPlaceholderText('Enter your password')
        self.txtPassword.setText('123')
        form.addWidget(QLabel('User name'))
        form.addWidget(self.txtUsername)
        form.addWidget(QLabel('Password'))
        form.addWidget(self.txtPassword)

        links = QHBoxLayout(); links.setSpacing(12)
        btnForgot = QPushButton('Forgot password?'); btnForgot.setObjectName('LinkButton')
        lblNoAccount = QLabel("Don't have an account?")
        btnSignup = QPushButton('Sign up'); btnSignup.setObjectName('LinkButton')
        btnSignup.clicked.connect(self.open_signup.emit)
        links.addWidget(btnForgot)
        links.addStretch()
        links.addWidget(lblNoAccount)
        links.addWidget(btnSignup)

        actions = QHBoxLayout(); actions.setSpacing(12)
        self.btnSignIn = QPushButton('Sign In'); self.btnSignIn.setObjectName('PrimaryButton')
        self.btnSignIn.clicked.connect(self.handle_login)
        self.txtPassword.returnPressed.connect(self.handle_login)
        actions.addWidget(self.btnSignIn)

        card.addLayout(form)
        card.addLayout(links)
        card.addLayout(actions)
        center.addStretch()
        center.addWidget(wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        center.addStretch()
        root.addLayout(center)
        self.setLayout(root)

    def handle_login(self):
        """Xử lý đăng nhập với username/password thực tế"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        
        if not username or not password:
            return
        
        try:
            db = get_db_connector()
            auth = AuthService(db)
            user = auth.login(username, password)
            
            if user:
                print(f"✓ Đăng nhập thành công: {user.username} ({user.role})")
                role = 'Admin' if user.role == 'Admin' else 'User'
                self.login_success.emit(SimpleUser(user.id, user.username, role))
            else:
                print(f"✗ Đăng nhập thất bại: Sai tên đăng nhập hoặc mật khẩu")
            
            db.close()
        except Exception as e:
            print(f"✗ Lỗi đăng nhập: {e}")

    def do_login(self, expected_admin: bool):
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        if not username or not password:
            return
        if AuthService is None:
            role = 'Admin' if expected_admin else 'User'
            self.login_success.emit(SimpleUser(1, username, role))
            return
        try:
            db = get_db_connector()
            auth = AuthService(db)
            user = auth.login(username, password)
            db.close()
        except Exception:
            user = None
        if user:
            role = 'Admin' if user.role == 'Admin' else 'User'
            self.login_success.emit(SimpleUser(user.id, user.username, role))
        else:
            role = 'Admin' if expected_admin else 'User'
            self.login_success.emit(SimpleUser(1, username or ('admin' if expected_admin else 'user'), role))

    def _prefill_and_login(self, expected_admin: bool):
        if expected_admin:
            self.txtUsername.setText('babyshark')
        else:
            self.txtUsername.setText('momshark')
        self.txtPassword.setText('123')
        self.do_login(expected_admin)
