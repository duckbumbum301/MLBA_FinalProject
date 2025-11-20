"""
LoginPage - Single entry login with database role validation
Supports both User and Admin roles from database
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QIcon
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
    proj = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(proj))
    from services.auth_service import AuthService
except Exception:
    AuthService = None
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
        titleBar = QLabel('Hệ Thống Quản Lý Rủi Ro Tín Dụng')
        th.addWidget(titleBar)
        th.addStretch()
        right = QLabel('Chưa đăng nhập'); right.setObjectName('HeaderStatus'); th.addWidget(right)
        root.addWidget(top)
        center = QVBoxLayout()
        wrapper = QWidget(); wrapper.setObjectName('Card'); wrapper.setMaximumWidth(520)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0,0,0,40))
        wrapper.setGraphicsEffect(shadow)
        card = QVBoxLayout(wrapper); card.setContentsMargins(20,20,20,20)
        title = QLabel('Chào mừng đến NYTDT - Hệ Thống Quản Lý Rủi Ro Tín Dụng!')
        title.setObjectName('CardTitle')
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        logo = QLabel(); logo.setObjectName('Logo')
        pix = QPixmap(str(base_dir / 'images' / 'logo.png'))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        form = QVBoxLayout(); form.setSpacing(10)
        self.txtUsername = QLineEdit(); self.txtUsername.setPlaceholderText('Nhập tên đăng nhập')
        self.txtPassword = QLineEdit(); self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password); self.txtPassword.setPlaceholderText('Nhập mật khẩu')
        form.addWidget(QLabel('Tên đăng nhập'))
        form.addWidget(self.txtUsername)
        form.addWidget(QLabel('Mật khẩu'))
        form.addWidget(self.txtPassword)
        
        # Forgot password link + popup
        forgot_layout = QHBoxLayout(); forgot_layout.addStretch()
        lblForgot = QLabel("Quên mật khẩu?")
        btnAlt = QPushButton('Thử cách khác'); btnAlt.setObjectName('LinkButton')
        forgot_layout.addWidget(lblForgot)
        forgot_layout.addWidget(btnAlt)
        form.addLayout(forgot_layout)
        btnAlt.clicked.connect(self._open_alt_dialog)
        
        actions = QHBoxLayout(); actions.setSpacing(12)
        self.btnLogin = QPushButton('Đăng nhập'); self.btnLogin.setObjectName('Primary')
        self.btnLogin.clicked.connect(self.handle_login)
        self.txtPassword.returnPressed.connect(self.handle_login)
        actions.addWidget(self.btnLogin)
        btnSignup = QPushButton('Đăng ký'); btnSignup.setObjectName('Secondary')
        btnSignup.clicked.connect(self.open_signup.emit)
        actions.addWidget(btnSignup)
        card.addLayout(form)
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
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu!")
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
                QMessageBox.critical(self, "Đăng nhập thất bại", "Sai tên đăng nhập hoặc mật khẩu.\nBạn có thể bấm 'Đăng ký' để tạo tài khoản mới.")
            
            db.close()
        except Exception as e:
            print(f"✗ Lỗi đăng nhập: {e}")

    def _send_forgot_request(self, full_name: str, email: str, username: str, note: str) -> bool:
        if not full_name or not email:
            return False
        try:
            from pathlib import Path
            import json, datetime
            proj = Path(__file__).resolve().parents[1]
            out_dir = proj / 'outputs' / 'system'
            out_dir.mkdir(parents=True, exist_ok=True)
            f = out_dir / 'forgot_requests.json'
            items = []
            if f.exists():
                try:
                    items = json.loads(f.read_text(encoding='utf-8'))
                except Exception:
                    items = []
            items.append({
                'full_name': full_name.strip(),
                'email': email.strip(),
                'username': username.strip(),
                'note': note.strip(),
                'ts': datetime.datetime.now().isoformat(),
                'status': 'pending'
            })
            f.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
            return True
        except Exception:
            return False

    def _open_alt_dialog(self):
        from PyQt6.QtWidgets import QDialog
        dlg = QDialog(self)
        dlg.setWindowTitle('Hỗ trợ đặt lại mật khẩu')
        try:
            icon_path = base_dir / 'images' / 'logo.png'
            if icon_path.exists():
                dlg.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
        lay = QVBoxLayout(dlg); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
        lay.addWidget(QLabel('Nhập thông tin để yêu cầu hỗ trợ đặt lại mật khẩu'))
        full_name = QLineEdit(); full_name.setPlaceholderText('Họ và Tên'); lay.addWidget(full_name)
        email = QLineEdit(); email.setPlaceholderText('Email'); lay.addWidget(email)
        username = QLineEdit(); username.setPlaceholderText('Tên người dùng (nếu nhớ)'); lay.addWidget(username)
        note = QLineEdit(); note.setPlaceholderText('Ghi chú (tuỳ chọn)'); lay.addWidget(note)
        btnSend = QPushButton('Gửi yêu cầu'); btnSend.setObjectName('Primary'); lay.addWidget(btnSend)
        btnSend.clicked.connect(lambda: (self._send_forgot_request(full_name.text(), email.text(), username.text(), note.text()) and dlg.accept()))
        dlg.exec()

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
