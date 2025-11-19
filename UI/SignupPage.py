"""
SignupPage - User registration with database storage
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QFrame, QSpacerItem, QSizePolicy, 
                              QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
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

class SignupPage(QWidget):
    go_login = pyqtSignal()
    signup_success = pyqtSignal()

    def __init__(self):
        super().__init__()
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
        wrapper.setMaximumWidth(520)
        wlay = QVBoxLayout(wrapper)
        wlay.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('Đăng ký tài khoản')
        title.setObjectName('CardTitle')
        wlay.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        
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
        btnBack.setObjectName('SecondaryButton')
        btnBack.clicked.connect(self.go_login.emit)
        actions.addWidget(btnBack)
        
        btnSignup = QPushButton('Đăng ký')
        btnSignup.setObjectName('PrimaryButton')
        btnSignup.clicked.connect(self.on_signup)
        actions.addWidget(btnSignup)
        
        wlay.addLayout(actions)
        
        center.addWidget(wrapper, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(center)
        self.setLayout(root)

    def on_signup(self):
        """Xử lý đăng ký tài khoản mới"""
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
        
        # Create user
        try:
            db = get_db_connector()
            auth = AuthService(db)
            
            success = auth.create_user(username, password, role)
            
            if success:
                QMessageBox.information(
                    self, 
                    "Thành công", 
                    f"Đã tạo tài khoản '{username}' với vai trò {role}!\n\nVui lòng đăng nhập."
                )
                print(f"✓ Đã đăng ký: {username} ({role})")
                self.clear_form()
                self.go_login.emit()
            else:
                QMessageBox.critical(
                    self, 
                    "Lỗi", 
                    f"Không thể tạo tài khoản!\nTên đăng nhập '{username}' có thể đã tồn tại."
                )
            
            db.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi đăng ký: {str(e)}")
            print(f"✗ Lỗi đăng ký: {e}")
    
    def clear_form(self):
        """Xóa form"""
        self.txtUsername.clear()
        self.txtPassword.clear()
        self.txtConfirm.clear()
        self.cmbRole.setCurrentIndex(0)
