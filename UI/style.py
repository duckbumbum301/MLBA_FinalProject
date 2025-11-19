STYLE_QSS = """
* { font-family: 'Inter','Segoe UI','Arial'; font-size: 16px; }
QMainWindow { background: #f7f9fc; }
QTabWidget::pane { border: 1px solid #dfe6ee; border-radius: 12px; background: white; }
QTabBar::tab { background: #eef3f8; color: #2c3e50; padding: 10px 20px; margin: 2px; border-radius: 8px; }
QTabBar::tab:selected { background: #2663ea; color: #ffffff; }

/* Button variants */
QPushButton { background-color: #2663ea; color: #ffffff; padding: 12px 18px; border-radius: 12px; font-weight: 700; }
QPushButton:hover { background-color: #1f54d8; }
QPushButton#Primary { background-color: #2663ea; color: #ffffff; padding: 12px 18px; border-radius: 12px; font-weight: 700; }
QPushButton#Primary:hover { background-color: #1f54d8; }
QPushButton#Secondary { background-color: #eef3f8; color: #2663ea; border: none; border-radius: 12px; padding: 12px 18px; font-weight: 700; }
QPushButton#Secondary:hover { background-color: #e1e8ef; color: #1f54d8; }
QPushButton#Danger { background-color: #D72638; color: #ffffff; }
QPushButton#Danger:hover { background-color: #b81f2d; }
QPushButton#Success { background-color: #2eb85d; color: #ffffff; }
QPushButton#Success:hover { background-color: #259c4f; }

/* Inputs */
QLabel { color: #2c3e50; font-family: 'Inter','Segoe UI','Arial'; font-size: 16px; }
QComboBox, QLineEdit, QTextEdit, QSpinBox, QTableWidget { background: #ffffff; border: 1px solid #dfe6ee; border-radius: 8px; padding: 8px; font-family: 'Inter','Segoe UI','Arial'; font-size: 16px; }
QComboBox:focus, QLineEdit:focus, QTextEdit:focus, QSpinBox:focus { border: 2px solid #2663ea; }
QHeaderView::section { background: #eef3f8; padding: 8px; border: 1px solid #dfe6ee; }

/* TopBar */
#TopBar { background: #2663ea; padding: 12px 18px; }
#TopBar QLabel { color: #ffffff; font-weight: 700; }
#HeaderStatus { color: #ecf0f1; }

/* Card */
#Card { background: #fff; border: 1px solid #dfe6ee; border-radius: 16px; padding: 20px; }
#CardTitle { font-size: 23px; font-weight: 700; margin: 8px 0 16px 0; color: #2c3e50; font-family: 'Poppins','Segoe UI','Arial'; }

/* Links */
#LinkButton { background: transparent; color: #2663ea; text-decoration: underline; border: none; padding: 0; }

/* GroupBox */
QGroupBox { background: #f7f9fc; border: 1px solid #dfe6ee; border-radius: 10px; margin-top: 12px; }
QGroupBox::title { color: #ffffff; background-color: #2663ea; padding: 4px 8px; border-radius: 6px; subcontrol-origin: margin; subcontrol-position: top left; font-family: 'Poppins','Segoe UI','Arial'; font-size: 23px; }
QLabel#SectionHeader { background: #2663ea; color: #eef3f8; font-family: 'Poppins','Segoe UI','Arial'; font-size: 16px; font-weight: 700; padding: 12px 18px; border-radius: 12px; margin: 0 0px 12px 0spx; }

QLineEdit { height: 34px; }
/* Navbar */
#NavBar { background: #ffffff; border-bottom: 1px solid #dfe6ee; padding: 10px 16px; }
#NavBar QLabel { color: #2c3e50; }
#NavBar QPushButton#NavItem { background: transparent; color: #2c3e50; padding: 8px 12px; border-radius: 8px; font-size: 17px; }
#NavBar QPushButton#NavItem:hover { background: #eef3f8; color: #2663ea; }
#NavBar QPushButton#NavItem:checked { background: #eef3f8; color: #2663ea; }
#NavBar QPushButton#AiButton { background: transparent; color: #2c3e50; padding: 0; border: none; min-width: 44px; min-height: 44px; }
#NavBar QPushButton#AiButton:hover { background: transparent; }
#NavBar QLineEdit#SearchBox { padding: 6px 10px; border: 1px solid #dfe6ee; border-radius: 8px; min-width: 240px; }
QLabel#Heading2 { font-family: 'Poppins','Segoe UI','Arial'; font-size: 25px; font-weight: 700; color: #ffffff; }
QLabel#Heading3 { font-family: 'Poppins','Segoe UI','Arial'; font-size: 20px; font-weight: 700; color: #2663ea; }
/* Footer */
#Footer { background: #f7f9fc; border-top: 1px solid #dfe6ee; padding: 8px 16px; }
#Footer QLabel { color: #6b778c; font-family: 'Inter','Segoe UI','Arial'; font-size: 16px; }
#Footer QLabel#FooterBrand { color: #2663ea; font-weight: 700; }
/* Dashboard */
#DashboardCardBlue { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #79B2F2, stop:1 #2F80ED); border: none; border-radius: 16px; }
#DashboardCardBlue QLabel#KpiTitle { color: #ffffff; font-family: 'Inter','Segoe UI','Arial'; font-size: 14px; }
#DashboardCardBlue QLabel#KpiValue { color: #ffffff; font-family: 'Poppins','Segoe UI','Arial'; font-size: 24px; font-weight: 700; }

#DashboardCardRed { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #F5A5A5, stop:1 #EB5757); border: none; border-radius: 16px; }
#DashboardCardRed QLabel#KpiTitle { color: #ffffff; font-family: 'Inter','Segoe UI','Arial'; font-size: 14px; }
#DashboardCardRed QLabel#KpiValue { color: #ffffff; font-family: 'Poppins','Segoe UI','Arial'; font-size: 24px; font-weight: 700; }

#DashboardCardYellow { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FAD7A0, stop:1 #F2994A); border: none; border-radius: 16px; }
#DashboardCardYellow QLabel#KpiTitle { color: #ffffff; font-family: 'Inter','Segoe UI','Arial'; font-size: 14px; }
#DashboardCardYellow QLabel#KpiValue { color: #ffffff; font-family: 'Poppins','Segoe UI','Arial'; font-size: 24px; font-weight: 700; }

#ChartCard { background: #ffffff; border: 1px solid #dfe6ee; border-radius: 16px; }
#ChartCard QLabel#ChartTitle { color: #2c3e50; font-family: 'Poppins','Segoe UI','Arial'; font-size: 16px; font-weight: 700; margin-bottom: 8px; }
#ChartCard QLabel#HealthDesc { color: #2c3e50; font-family: 'Inter','Segoe UI','Arial'; font-size: 14px; }
QLabel#ChipWarning { background: #fdecef; color: #EB5757; border-radius: 10px; padding: 2px 10px; font-family: 'Inter','Segoe UI','Arial'; font-size: 13px; font-weight: 700; }
QLabel#ChipStable { background: #eaf6ed; color: #27AE60; border-radius: 10px; padding: 2px 10px; font-family: 'Inter','Segoe UI','Arial'; font-size: 13px; font-weight: 700; }
"""
