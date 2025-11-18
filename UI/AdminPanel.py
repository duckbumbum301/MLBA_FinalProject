from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from pathlib import Path
import sys
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))
try:
    from theme import PALETTE_LIGHT, PALETTE_DARK, build_qss
except Exception:
    from .theme import PALETTE_LIGHT, PALETTE_DARK, build_qss

try:
    from .admin_pages.DashboardPage import DashboardPage
    from .admin_pages.ModelLabPage import ModelLabPage
    from .admin_pages.DataQualityPage import DataQualityPage
    from .admin_pages.CopilotPage import CopilotPage
except Exception:
    from admin_pages.DashboardPage import DashboardPage
    from admin_pages.ModelLabPage import ModelLabPage
    from admin_pages.DataQualityPage import DataQualityPage
    from admin_pages.CopilotPage import CopilotPage

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('AdminRoot')
        self.palette_mode = 'light'
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        self.sidebar = QFrame(); self.sidebar.setObjectName('Sidebar')
        sb = QVBoxLayout(self.sidebar); sb.setContentsMargins(12,12,12,12)
        self.btnDashboard = QPushButton('  Dashboard'); self.btnDashboard.setObjectName('SideItem')
        self.btnModelLab = QPushButton('  Model Lab'); self.btnModelLab.setObjectName('SideItem')
        self.btnDataQuality = QPushButton('  Data Quality'); self.btnDataQuality.setObjectName('SideItem')
        self.btnCopilot = QPushButton('  AI Copilot'); self.btnCopilot.setObjectName('SideItem')
        self.btnLogout = QPushButton('  Logout'); self.btnLogout.setObjectName('SideItem')
        for b in [self.btnDashboard, self.btnModelLab, self.btnDataQuality, self.btnCopilot, self.btnLogout]:
            sb.addWidget(b)
        sb.addStretch()
        self.content = QVBoxLayout(); self.content.setContentsMargins(0,0,0,0)
        self.navbar = QFrame(); self.navbar.setObjectName('Navbar')
        nb = QHBoxLayout(self.navbar); nb.setContentsMargins(16,10,16,10)
        self.navTitle = QLabel('Admin Control Panel'); self.navTitle.setObjectName('NavbarTitle')
        nb.addWidget(self.navTitle); nb.addStretch()
        self.btnTheme = QPushButton('Dark'); self.btnTheme.setObjectName('Secondary')
        nb.addWidget(self.btnTheme)
        self.stack = QStackedWidget()
        self.pageDashboard = DashboardPage()
        self.pageModelLab = ModelLabPage()
        self.pageDataQuality = DataQualityPage()
        self.pageCopilot = CopilotPage()
        self.stack.addWidget(self.pageDashboard)
        self.stack.addWidget(self.pageModelLab)
        self.stack.addWidget(self.pageDataQuality)
        self.stack.addWidget(self.pageCopilot)
        self.content.addWidget(self.navbar)
        self.content.addWidget(self.stack)
        root.addWidget(self.sidebar, 0)
        wrap = QFrame(); wl = QVBoxLayout(wrap); wl.setContentsMargins(0,0,0,0); wl.addLayout(self.content)
        root.addWidget(wrap, 1)
        self.btnDashboard.clicked.connect(lambda: self.switch_page(0, self.btnDashboard))
        self.btnModelLab.clicked.connect(lambda: self.switch_page(1, self.btnModelLab))
        self.btnDataQuality.clicked.connect(lambda: self.switch_page(2, self.btnDataQuality))
        self.btnCopilot.clicked.connect(lambda: self.switch_page(3, self.btnCopilot))
        self.btnTheme.clicked.connect(self.toggle_theme)
        self.switch_page(0, self.btnDashboard)

    def switch_page(self, index, active_btn):
        self.stack.setCurrentIndex(index)
        for b in [self.btnDashboard, self.btnModelLab, self.btnDataQuality, self.btnCopilot, self.btnLogout]:
            b.setProperty('class', '')
            b.style().unpolish(b); b.style().polish(b)
        active_btn.setProperty('class', 'active')
        active_btn.style().unpolish(active_btn); active_btn.style().polish(active_btn)

    def toggle_theme(self):
        self.palette_mode = 'dark' if self.palette_mode == 'light' else 'light'
        self.apply_theme()
        self.btnTheme.setText('Light' if self.palette_mode=='dark' else 'Dark')

    def apply_theme(self):
        p = PALETTE_DARK if self.palette_mode=='dark' else PALETTE_LIGHT
        self.setStyleSheet(build_qss(p))

