"""
Credit Risk Scoring System - Main Entry Point
Chạy: python main.py hoặc py -3.12 main.py
"""
import sys
from pathlib import Path

<<<<<<< Updated upstream
=======
from ui.LoginPage import LoginPage
from ui.MainWindow import MainWindow

>>>>>>> Stashed changes
# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from ui.LoginPage import LoginPage
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
        self.main_window.show()


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
    try:
        rc = app.exec()
    except KeyboardInterrupt:
        rc = 0
    sys.exit(rc)


if __name__ == '__main__':
    main()
