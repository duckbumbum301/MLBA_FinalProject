from PyQt6.QtWidgets import QMainWindow, QTabWidget
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from .user_model import User
    from .PredictionTab import PredictionTab
    from .ReportTab import ReportTab
    from .AIAssistantTab import AIAssistantTab
    from .ModelManagementTab import ModelManagementTab
    from .SystemManagementTab import SystemManagementTab
except Exception:
    from user_model import User
    from PredictionTab import PredictionTab
    from ReportTab import ReportTab
    from AIAssistantTab import AIAssistantTab
    from ModelManagementTab import ModelManagementTab
    from SystemManagementTab import SystemManagementTab

try:
    from .style import STYLE_QSS
except Exception:
    from style import STYLE_QSS

try:
    from .CustomerEntryTab import CustomerEntryTab
except Exception:
    from CustomerEntryTab import CustomerEntryTab

class MainWindow(QMainWindow):
    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Credit Risk System - {self.user.username} ({self.user.role})")
        self.tab = QTabWidget()
        self.setCentralWidget(self.tab)
        self.setStyleSheet(STYLE_QSS)
        self.setup_tabs()

    def setup_tabs(self):
        self.prediction_tab = PredictionTab(self.user)
        self.report_tab = ReportTab(self.user)
        self.ai_tab = AIAssistantTab()
        self.customer_tab = CustomerEntryTab(self.user.id)
        self.tab.addTab(self.prediction_tab, 'Dự Báo')
        self.tab.addTab(self.report_tab, 'Báo Cáo')
        self.tab.addTab(self.ai_tab, 'AI Trợ Lý')
        self.tab.addTab(self.customer_tab, 'Khách Hàng')
        if self.user.is_admin():
            self.ml_tab = ModelManagementTab()
            self.sys_tab = SystemManagementTab()
            self.tab.addTab(self.ml_tab, 'Quản Lý ML')
            self.tab.addTab(self.sys_tab, 'Hệ Thống')
