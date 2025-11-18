from PyQt6.QtGui import QColor

PALETTE_LIGHT = {
    'bg': '#F5F7FA',
    'surface': '#FFFFFF',
    'navy': '#0A2A43',
    'blue': '#1A73E8',
    'muted': '#E3ECF4',
    'danger': '#D72638',
    'text': '#10151A'
}

PALETTE_DARK = {
    'bg': '#0A2A43',
    'surface': '#10151A',
    'navy': '#F5F7FA',
    'blue': '#1A73E8',
    'muted': '#101a26',
    'danger': '#D72638',
    'text': '#E3ECF4'
}

def build_qss(p):
    return f"""
    QWidget#AdminRoot {{ background: {p['bg']}; }}
    QFrame#Navbar {{ background: {p['surface']}; border-bottom: 1px solid {p['muted']}; }}
    QLabel#NavbarTitle {{ color: {p['navy']}; font-weight: 700; }}
    QFrame#Sidebar {{ background: {p['surface']}; border-right: 1px solid {p['muted']}; }}
    QPushButton#SideItem {{ background: transparent; color: {p['navy']}; padding: 10px; text-align: left; border-radius: 8px; }}
    QPushButton#SideItem:hover {{ background: {p['muted']}; }}
    QPushButton#SideItem.active {{ background: {p['blue']}; color: #fff; }}
    QFrame#Card {{ background: {p['surface']}; border: 1px solid {p['muted']}; border-radius: 12px; }}
    QLabel#CardTitle {{ color: {p['navy']}; font-weight: 700; }}
    QPushButton#Primary {{ background: {p['blue']}; color: #fff; padding: 8px 14px; border-radius: 8px; font-weight: 600; }}
    QPushButton#Secondary {{ background: {p['muted']}; color: {p['navy']}; padding: 8px 14px; border-radius: 8px; font-weight: 600; }}
    QSlider::groove:horizontal {{ height: 6px; background: {p['muted']}; border-radius: 3px; }}
    QSlider::handle:horizontal {{ width: 14px; background: {p['blue']}; margin: -4px 0; border-radius: 7px; }}
    QTableWidget {{ background: {p['surface']}; border: 1px solid {p['muted']}; border-radius: 8px; }}
    QHeaderView::section {{ background: {p['muted']}; padding: 6px; border: none; }}
    """

