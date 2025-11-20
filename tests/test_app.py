"""
Test App - Entry Point
Main script để chạy ứng dụng Credit Risk Scoring System

Usage:
    python -m tests.test_app
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from UI.LoginPage import LoginPage
from UI.MainWindow import MainWindow
from UI.user_model import User as SimpleUser


class CreditRiskApp:
    """
    Main Application Controller
    Quản lý flow: Login -> MainWindow -> Logout -> Login
    """
    
    def __init__(self):
        """Khởi tạo application"""
        self.login_window = None
        self.main_window = None
    
    def start(self):
        """Bắt đầu ứng dụng với màn hình login"""
        self.show_login()
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginPage()
        
        # Connect signal login thành công
        self.login_window.login_success.connect(self.on_login_successful)
        
        # Show login window
        self.login_window.show()
    
    def on_login_successful(self, user):
        """
        Callback khi đăng nhập thành công
        
        Args:
            user: User object đã đăng nhập
        """
        print(f"\n{'='*60}")
        print(f"✓ LOGIN SUCCESSFUL")
        print(f"{'='*60}")
        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print(f"{'='*60}\n")
        
        # Đóng login window
        self.login_window.close()
        
        # Mở main window
        self.show_main_window(user)
    
    def show_main_window(self, user):
        """
        Hiển thị main window
        
        Args:
            user: User object
        """
        self.main_window = MainWindow(user)
        
        # Connect signal logout nếu có
        # self.main_window.logout_signal.connect(self.on_logout)
        
        # Show main window
        self.main_window.show()
    
    def on_logout(self):
        """Callback khi logout"""
        print(f"\n{'='*60}")
        print(f"✓ LOGOUT")
        print(f"{'='*60}\n")
        
        # Đóng main window
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Quay lại login
        self.show_login()


def main():
    """Main function"""
    print("\n" + "="*60)
    print("CREDIT RISK SCORING SYSTEM")
    print("="*60)
    print("Starting application...")
    print("="*60 + "\n")
    
    # Tạo QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Credit Risk Scoring System")
    app.setOrganizationName("BabyShark Banking")
    
    # Tạo và start app controller
    credit_app = CreditRiskApp()
    credit_app.start()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
