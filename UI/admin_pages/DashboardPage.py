from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def card(self, title, value):
        f = QFrame(); f.setObjectName('Card')
        l = QVBoxLayout(f)
        t = QLabel(title); t.setObjectName('CardTitle')
        v = QLabel(value); v.setAlignment(Qt.AlignmentFlag.AlignRight)
        l.addWidget(t); l.addWidget(v)
        return f

    def setup_ui(self):
        root = QVBoxLayout(self)
        grid = QGridLayout(); grid.setSpacing(12)
        grid.addWidget(self.card('Active Model', 'XGBoost_v3'), 0,0)
        grid.addWidget(self.card('Best AUC', '0.88'), 0,1)
        grid.addWidget(self.card('Predictions Today', '124'), 0,2)
        grid.addWidget(self.card('System Health', 'OK'), 0,3)
        root.addLayout(grid)
        perf = QHBoxLayout()
        roc = QFrame(); roc.setObjectName('Card'); rocLay = QVBoxLayout(roc); rocLay.addWidget(QLabel('ROC'))
        pr = QFrame(); pr.setObjectName('Card'); prLay = QVBoxLayout(pr); prLay.addWidget(QLabel('PR'))
        dr = QFrame(); dr.setObjectName('Card'); drLay = QVBoxLayout(dr); drLay.addWidget(QLabel('Default Rate Trend'))
        perf.addWidget(roc); perf.addWidget(pr); perf.addWidget(dr)
        root.addLayout(perf)
        alerts = QFrame(); alerts.setObjectName('Card'); al = QVBoxLayout(alerts); al.addWidget(QLabel('Alerts')); al.addWidget(QLabel('• Cluster 3 default rate 71.8%'))
        root.addWidget(alerts)

