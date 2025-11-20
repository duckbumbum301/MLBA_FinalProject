"""
SignupPage - User registration with database storage
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QFrame, QSpacerItem, QSizePolicy, 
                              QMessageBox, QComboBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from pathlib import Path
import sys

base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

try:
    from integration import get_db_connector
except Exception:
    from .integration import get_db_connector

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

class SignupPage(QWidget):
    go_login = pyqtSignal()
    signup_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        try:
            self.setStyleSheet(STYLE_QSS)
        except Exception:
            pass
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('SignupPage')
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(0, 0, 0, 0)
        
        # Top bar
        top = QFrame()
        top.setObjectName('TopBar')
        th = QHBoxLayout(top)
        th.setContentsMargins(16, 8, 16, 8)
        th.addWidget(QLabel('Hệ Thống Quản Lý Rủi Ro Tín Dụng'))
        th.addStretch()
        status = QLabel('Đăng ký tài khoản mới')
        status.setObjectName('HeaderStatus')
        th.addWidget(status)
        root.addWidget(top)
        
        root.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Center content
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignTop)
        wrapper = QWidget()
        wrapper.setObjectName('Card')
        wrapper.setMaximumWidth(720)
        try:
            wrapper.setMinimumWidth(580)
        except Exception:
            pass
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0,0,0,40))
        wrapper.setGraphicsEffect(shadow)
        wlay = QVBoxLayout(wrapper)
        wlay.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('Đăng ký tài khoản')
        title.setObjectName('CardTitle')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wlay.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        logo = QLabel()
        pix = QPixmap(str(base_dir / 'images' / 'logo.png'))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        wlay.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Form
        form = QVBoxLayout()
        form.setSpacing(10)
        
        form.addWidget(QLabel('Tên đăng nhập'))
        self.txtUsername = QLineEdit()
        self.txtUsername.setPlaceholderText('Nhập tên đăng nhập (3-20 ký tự)')
        form.addWidget(self.txtUsername)
        
        form.addWidget(QLabel('Mật khẩu'))
        self.txtPassword = QLineEdit()
        self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.txtPassword.setPlaceholderText('Nhập mật khẩu (tối thiểu 3 ký tự)')
        form.addWidget(self.txtPassword)
        
        form.addWidget(QLabel('Xác nhận mật khẩu'))
        self.txtConfirm = QLineEdit()
        self.txtConfirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.txtConfirm.setPlaceholderText('Nhập lại mật khẩu')
        self.txtConfirm.returnPressed.connect(self.on_signup)
        form.addWidget(self.txtConfirm)
        
        form.addWidget(QLabel('Vai trò'))
        self.cmbRole = QComboBox()
        self.cmbRole.addItems(['User', 'Admin'])
        form.addWidget(self.cmbRole)
        
        wlay.addLayout(form)
        
        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(12)
        
        btnBack = QPushButton('Quay lại')
        btnBack.setObjectName('Secondary')
        btnBack.clicked.connect(self.go_login.emit)
        actions.addWidget(btnBack)
        
        btnSignup = QPushButton('Đăng ký')
        btnSignup.setObjectName('Primary')
        btnSignup.clicked.connect(self.on_signup)
        actions.addWidget(btnSignup)
        
        wlay.addLayout(actions)
        
        center.addWidget(wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(center)
        self.setLayout(root)

    def on_signup(self):
        """Gửi yêu cầu đăng ký tài khoản mới (chờ duyệt)"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        confirm = self.txtConfirm.text()
        role = self.cmbRole.currentText()
        
        # Validation
        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return
        if len(username) < 3 or len(username) > 20:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập phải từ 3-20 ký tự!")
            return
        if len(password) < 3:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 3 ký tự!")
            return
        if password != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        # Lưu yêu cầu đăng ký để admin duyệt
        try:
            proj = Path(__file__).resolve().parents[1]
            out_dir = proj / 'outputs' / 'system'
            out_dir.mkdir(parents=True, exist_ok=True)
            f = out_dir / 'signup_requests.json'
            items = []
            if f.exists():
                import json
                try:
                    items = json.loads(f.read_text(encoding='utf-8'))
                except Exception:
                    items = []
            from datetime import datetime
            items.append({
                'username': username,
                'password': password,
                'role': role,
                'ts': datetime.now().isoformat(),
                'status': 'pending'
            })
            import json
            f.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
            QMessageBox.information(self, "Thành công", "Đã gửi yêu cầu đăng ký! Vui lòng chờ admin duyệt.")
            self.clear_form()
            self.go_login.emit()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể gửi yêu cầu đăng ký: {str(e)}")
    
    def clear_form(self):
        """Xóa form"""
        self.txtUsername.clear()
        self.txtPassword.clear()
        self.txtConfirm.clear()
        self.cmbRole.setCurrentIndex(0)
