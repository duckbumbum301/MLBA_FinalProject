from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    proj = Path(__file__).resolve().parents[1] / 'MLBA_FinalProject'
    sys.path.insert(0, str(proj))
    from services.auth_service import AuthService
    from integration import get_db_connector
except Exception:
    AuthService = None
    def get_db_connector():
        return None

class SignupPage(QWidget):
    go_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(); root.setAlignment(Qt.AlignmentFlag.AlignTop); root.setContentsMargins(0,0,0,0)
        top = QFrame(); top.setObjectName('TopBar'); th = QHBoxLayout(top); th.setContentsMargins(16,8,16,8)
        th.addWidget(QLabel('Credit Risk Management System'))
        th.addStretch(); th.addWidget(QLabel('Not logged in'))
        root.addWidget(top)
        root.addSpacerItem(QSpacerItem(20,40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        center = QVBoxLayout(); center.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper = QWidget(); wrapper.setObjectName('Card'); wrapper.setMaximumWidth(520)
        wlay = QVBoxLayout(wrapper); wlay.setContentsMargins(20,20,20,20)
        title = QLabel('Welcome to NYTDT - Credit Risk Management System!'); title.setObjectName('CardTitle')
        form = QVBoxLayout(); form.setSpacing(10)
        self.txtFullName = QLineEdit(); self.txtFullName.setPlaceholderText('Enter your full name')
        self.txtEmail = QLineEdit(); self.txtEmail.setPlaceholderText('Enter your email')
        self.txtPassword = QLineEdit(); self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password); self.txtPassword.setPlaceholderText('Enter your password')
        self.txtConfirm = QLineEdit(); self.txtConfirm.setEchoMode(QLineEdit.EchoMode.Password); self.txtConfirm.setPlaceholderText('Confirm your password')
        form.addWidget(QLabel('Full name')); form.addWidget(self.txtFullName)
        form.addWidget(QLabel('Email')); form.addWidget(self.txtEmail)
        form.addWidget(QLabel('Password')); form.addWidget(self.txtPassword)
        form.addWidget(QLabel('Confirm your password')); form.addWidget(self.txtConfirm)
        actions = QHBoxLayout(); actions.setSpacing(12)
        btnSignup = QPushButton('Sign up'); btnSignup.setObjectName('PrimaryButton'); btnSignup.clicked.connect(self.on_signup)
        actions.addWidget(btnSignup)
        actions.addStretch()
        loginLink = QPushButton('Log in'); loginLink.setObjectName('LinkButton'); loginLink.clicked.connect(lambda: self.go_login.emit())
        actions.addWidget(QLabel("Don't have an account?"))
        actions.addWidget(loginLink)
        wlay.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        wlay.addLayout(form)
        wlay.addLayout(actions)
        center.addWidget(wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(center)
        self.setLayout(root)

    def on_signup(self):
        name = self.txtFullName.text().strip()
        pwd = self.txtPassword.text()
        cf = self.txtConfirm.text()
        if not name or not pwd or pwd != cf:
            return
        if AuthService is None:
            self.go_login.emit()
            return
        db = get_db_connector()
        auth = AuthService(db)
        auth.create_user(username=name, password=pwd, role='Secretary')
        db.close()
        self.go_login.emit()
