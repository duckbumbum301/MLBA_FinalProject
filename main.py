"""
Credit Risk Scoring System - Main Entry Point
Chạy: python main.py hoặc py -3.12 main.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QStackedWidget
from ui.LoginPage import LoginPage
from ui.SignupPage import SignupPage
from ui.MainWindow import MainWindow
from ui.user_model import User as SimpleUser


class CreditRiskApp:
    """Main Application Controller"""
    
    def __init__(self):
        self.stack = QStackedWidget()
        self.login_window = None
        self.signup_window = None
        self.main_window = None
    
    def start(self):
        """Bắt đầu với màn hình login"""
        self.show_login()
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginPage()
        self.login_window.login_success.connect(self.on_login_successful)
        self.login_window.open_signup.connect(self.show_signup)
        self.login_window.show()
    
    def show_signup(self):
        """Hiển thị màn hình đăng ký"""
        if self.login_window:
            self.login_window.close()
        
        self.signup_window = SignupPage()
        self.signup_window.go_login.connect(self.show_login)
        self.signup_window.show()
    
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
        if self.signup_window:
            self.signup_window.close()
        
        self.main_window = MainWindow(user)
        self.main_window.logout_signal.connect(self.on_logout)
        self.main_window.show()
    
    def on_logout(self):
        """Callback khi đăng xuất"""
        print("\n✓ Đã đăng xuất, quay về màn hình đăng nhập\n")
        if self.main_window:
            self.main_window.close()
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
    
    credit_app = CreditRiskApp()
    credit_app.start()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
