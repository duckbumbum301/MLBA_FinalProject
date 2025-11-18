STYLE_QSS = """
QMainWindow { background: #f5f7fb; }
QTabWidget::pane { border: 1px solid #dfe6ee; border-radius: 10px; background: white; }
QTabBar::tab { background: #eef3f8; padding: 8px 18px; margin: 2px; border-radius: 8px; }
QTabBar::tab:selected { background: #2f80ed; color: white; }

QLabel { color: #1f2937; }
QComboBox, QLineEdit, QTextEdit, QSpinBox, QTableWidget {
  background: #ffffff; border: 2px solid #e6edf5; border-radius: 10px; padding: 10px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus {
  border: 2px solid #2f80ed;
}
QHeaderView::section { background: #eef3f8; padding: 8px; border: 1px solid #dfe6ee; }

/* Top bar gradient */
#TopBar {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    stop:0 #2f80ed, stop:1 #5fa8ff);
  padding: 12px 20px;
}
#TopBar * { background: transparent; }
#TopBar QLabel { color: #fff; font-weight: 600; }
#HeaderStatus { color: #ecf0f1; }

/* Card */
#Card { background: #fff; border: 1px solid #e6edf5; border-radius: 18px; padding: 24px; }
#CardTitle { font-size: 22px; font-weight: 800; margin: 8px 0 18px 0; color: #1f2937; }

/* Links */
#LinkButton { background: transparent; color: #2f80ed; text-decoration: underline; border: none; padding: 0; }

/* Buttons */
QPushButton { font-weight: 700; border-radius: 10px; }
#PrimaryButton { background: #2f80ed; color: #fff; padding: 12px 24px; }
#PrimaryButton:hover { background: #1f6fd1; }
#PrimaryButton:pressed { background: #1a5ec0; }
#SecondaryButton { background: #eef3f8; color: #2c3e50; padding: 12px 24px; }
#SecondaryButton:hover { background: #e1e8ef; }

QLineEdit { height: 40px; font-size: 14px; padding-left: 12px; }
QLabel { font-size: 14px; }
"""
