from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem

class DataQualityPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        outliers = QFrame(); outliers.setObjectName('Card'); ol = QVBoxLayout(outliers)
        ol.addWidget(QLabel('Phát hiện ngoại lệ'))
        self.table = QTableWidget(5,5)
        self.table.setHorizontalHeaderLabels(['Mã khách','Đặc trưng','Giá trị','Điểm','Hành động'])
        for i in range(5):
            self.table.setItem(i,0,QTableWidgetItem(str(1000+i)))
            self.table.setItem(i,1,QTableWidgetItem('BILL_AMT6'))
            self.table.setItem(i,2,QTableWidgetItem('56000'))
            self.table.setItem(i,3,QTableWidgetItem('0.92'))
            self.table.setItem(i,4,QTableWidgetItem('Gắn cờ'))
        btns = QHBoxLayout(); btns.addWidget(QPushButton('Chạy quét')); btns.addWidget(QPushButton('Xuất CSV'))
        ol.addWidget(self.table); ol.addLayout(btns)
        cluster = QFrame(); cluster.setObjectName('Card'); cl = QVBoxLayout(cluster)
        cl.addWidget(QLabel('Phân cụm khách hàng'))
        cl.addWidget(QLabel('Phân tán PCA 2-D (minh họa)'))
        cl.addWidget(QLabel('Tóm tắt: Thấp/Trung bình/Cao/Cực kỳ cao'))
        root.addWidget(outliers,1); root.addWidget(cluster,1)

