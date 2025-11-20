"""
Credit Risk Scoring System - Main Entry Point
Chạy: python main.py hoặc py -3.12 main.py
"""
import sys
from pathlib import Path
# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.LoginPage import LoginPage
from ui.SignupPage import SignupPage
from ui.MainWindow import MainWindow
from ui.user_model import User as SimpleUser


class CreditRiskApp:
    """Main Application Controller"""
    
    def __init__(self):
        self.login_window = None
        self.main_window = None
    
    def start(self):
        """Bắt đầu với màn hình login"""
        self.show_login()
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginPage()
        self.login_window.login_success.connect(self.on_login_successful)
        try:
            self.login_window.open_signup.connect(self.show_signup)
        except Exception:
            pass
        self.login_window.show()
    
    def on_login_successful(self, user):
        """Callback khi đăng nhập thành công"""
        print(f"\n{'='*60}")
        print(f"✓ LOGIN SUCCESSFUL")
        print(f"{'='*60}")
        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print(f"{'='*60}\n")
        
        self.login_window.close()
        self.show_main_window(user)
    
    def show_main_window(self, user):
        """Hiển thị main window"""
        self.main_window = MainWindow(user)
        try:
            self.main_window.logout_signal.connect(self.on_logged_out)
        except Exception:
            pass
        self.main_window.show()

    def show_signup(self):
        """Mở màn hình đăng ký"""
        try:
            self.login_window.close()
        except Exception:
            pass
        self.signup_window = SignupPage()
        try:
            self.signup_window.go_login.connect(self.show_login)
            self.signup_window.signup_success.connect(self.show_login)
        except Exception:
            pass
        self.signup_window.show()

    def on_logged_out(self):
        """Quay lại màn hình đăng nhập khi user đăng xuất"""
        try:
            if self.main_window:
                self.main_window.close()
        except Exception:
            pass
        self.main_window = None
        self.show_login()


def main():
    """Main function"""
    print("\n" + "="*60)
    print("CREDIT RISK SCORING SYSTEM")
    print("="*60)
    print("Starting application...")
    print("="*60 + "\n")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Credit Risk Scoring System")
    app.setOrganizationName("BabyShark Banking")
    try:
        icon_path = project_root / 'UI' / 'images' / 'logo.png'
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass
    
    credit_app = CreditRiskApp()
    credit_app.start()
    try:
        rc = app.exec()
    except KeyboardInterrupt:
        rc = 0
    sys.exit(rc)


if __name__ == '__main__':
    main()
