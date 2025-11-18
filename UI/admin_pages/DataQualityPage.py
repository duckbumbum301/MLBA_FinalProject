from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem

class DataQualityPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        outliers = QFrame(); outliers.setObjectName('Card'); ol = QVBoxLayout(outliers)
        ol.addWidget(QLabel('Outlier Detection'))
        self.table = QTableWidget(5,5)
        self.table.setHorizontalHeaderLabels(['customer_id','feature','value','score','actions'])
        for i in range(5):
            self.table.setItem(i,0,QTableWidgetItem(str(1000+i)))
            self.table.setItem(i,1,QTableWidgetItem('BILL_AMT6'))
            self.table.setItem(i,2,QTableWidgetItem('56000'))
            self.table.setItem(i,3,QTableWidgetItem('0.92'))
            self.table.setItem(i,4,QTableWidgetItem('Flag'))
        btns = QHBoxLayout(); btns.addWidget(QPushButton('Run Scan')); btns.addWidget(QPushButton('Export CSV'))
        ol.addWidget(self.table); ol.addLayout(btns)
        cluster = QFrame(); cluster.setObjectName('Card'); cl = QVBoxLayout(cluster)
        cl.addWidget(QLabel('Customer Clustering'))
        cl.addWidget(QLabel('PCA 2-D scatter (placeholder)'))
        cl.addWidget(QLabel('Summary: Low/Med/High/Critical'))
        root.addWidget(outliers,1); root.addWidget(cluster,1)

