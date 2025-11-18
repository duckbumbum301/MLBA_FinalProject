import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
base_dir = Path(__file__).resolve().parent
project_root = base_dir.parent.parent
external_ui = project_root / 'UI'
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(external_ui))
try:
    from user_model import User
    from MainWindow import MainWindow
    from LoginPage import LoginPage
    from SignupPage import SignupPage
    from style import STYLE_QSS
    from AdminPanel import AdminPanel
except Exception:
    from .user_model import User
    from .MainWindow import MainWindow
    from .LoginPage import LoginPage
    from .SignupPage import SignupPage
    from .style import STYLE_QSS
    from .AdminPanel import AdminPanel

def main():
    app = QApplication(sys.argv)
    shell = QMainWindow()
    shell.setWindowTitle('Credit Risk Management System')
    shell.setStyleSheet(STYLE_QSS)
    lp = LoginPage()
    sp = SignupPage()
    def show_login():
        shell.setCentralWidget(lp)
        shell.resize(1000, 600)
        shell.show()
    def show_signup():
        shell.setCentralWidget(sp)
        shell.resize(1000, 600)
        shell.show()
    def on_login(simple_user: User):
        if simple_user.is_admin():
            w = QMainWindow(); panel = AdminPanel(); w.setCentralWidget(panel); w.resize(1280, 800); w.show()
        else:
            w = MainWindow(simple_user); w.resize(1000, 700); w.show()
        shell.close()
    lp.open_signup.connect(show_signup)
    lp.login_success.connect(on_login)
    sp.go_login.connect(show_login)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['admin', 'user']:
        role = 'Admin' if sys.argv[1].lower()=='admin' else 'User'
        if role=='Admin':
            w = QMainWindow(); panel = AdminPanel(); w.setCentralWidget(panel); w.resize(1280, 800); w.show()
        else:
            w = MainWindow(User(1, 'demo', role)); w.resize(1000, 700); w.show()
    else:
        show_login()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
