from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
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
try:
    proj = Path(__file__).resolve().parents[1] / 'MLBA_FinalProject'
    sys.path.insert(0, str(proj))
    from services.auth_service import AuthService
except Exception:
    AuthService = None

class LoginPage(QWidget):
    login_success = pyqtSignal(SimpleUser)
    open_signup = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('LoginPage')
        root = QVBoxLayout(); root.setAlignment(Qt.AlignmentFlag.AlignTop); root.setContentsMargins(0,0,0,0)
        top = QFrame(); top.setObjectName('TopBar'); th = QHBoxLayout(top); th.setContentsMargins(16,8,16,8)
        titleBar = QLabel('Credit Risk Management System')
        th.addWidget(titleBar)
        th.addStretch()
        right = QLabel('Not logged in'); right.setObjectName('HeaderStatus'); th.addWidget(right)
        root.addWidget(top)
        root.addSpacerItem(QSpacerItem(20,40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        center = QVBoxLayout(); center.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper = QWidget(); wrapper.setObjectName('Card'); wrapper.setMaximumWidth(520)
        card = QVBoxLayout(wrapper); card.setContentsMargins(20,20,20,20)
        title = QLabel('Welcome to NYTDT - Credit Risk Management System!')
        title.setObjectName('CardTitle')
        card.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        form = QVBoxLayout(); form.setSpacing(10)
        self.txtUsername = QLineEdit(); self.txtUsername.setPlaceholderText('Enter your user name')
        self.txtPassword = QLineEdit(); self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password); self.txtPassword.setPlaceholderText('Enter your password')
        form.addWidget(QLabel('User name'))
        form.addWidget(self.txtUsername)
        form.addWidget(QLabel('Password'))
        form.addWidget(self.txtPassword)
        links = QHBoxLayout(); links.setContentsMargins(0,0,0,0)
        forgot = QPushButton('Forgot password?'); forgot.setObjectName('LinkButton')
        signup = QPushButton('Sign up'); signup.setObjectName('LinkButton')
        signup.clicked.connect(lambda: self.open_signup.emit())
        links.addWidget(forgot)
        links.addStretch()
        links.addWidget(QLabel("Don't have an account?"))
        links.addWidget(signup)
        form.addLayout(links)
        actions = QHBoxLayout(); actions.setSpacing(12)
        self.btnUser = QPushButton('Log in as User'); self.btnUser.setObjectName('PrimaryButton')
        self.btnAdmin = QPushButton('Log in as Admin'); self.btnAdmin.setObjectName('SecondaryButton')
        self.btnUser.clicked.connect(lambda: self._prefill_and_login(False))
        self.btnAdmin.clicked.connect(lambda: self._prefill_and_login(True))
        actions.addWidget(self.btnUser)
        actions.addWidget(self.btnAdmin)
        card.addLayout(form)
        card.addLayout(actions)
        center.addWidget(wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(center)
        self.setLayout(root)

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
