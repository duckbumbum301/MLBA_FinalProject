from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem

class CopilotPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        chat = QFrame(); chat.setObjectName('Card'); ch = QVBoxLayout(chat)
        ch.addWidget(QLabel('Trợ lý rủi ro AI'))
        self.input = QTextEdit(); self.input.setPlaceholderText('Hỏi: Giải thích mô hình, ngưỡng, tóm tắt dự báo...')
        actions = QHBoxLayout(); actions.addWidget(QPushButton('Giải thích mô hình')); actions.addWidget(QPushButton('Giải thích ngưỡng')); actions.addWidget(QPushButton('Tóm tắt 100 dự báo'))
        ch.addWidget(self.input); ch.addLayout(actions)
        history = QFrame(); history.setObjectName('Card'); hh = QVBoxLayout(history)
        hh.addWidget(QLabel('Lịch sử chat'))
        table = QTableWidget(5,3); table.setHorizontalHeaderLabels(['Thời gian','Yêu cầu','Hành động'])
        for i in range(5):
            table.setItem(i,0,QTableWidgetItem('10:20'))
            table.setItem(i,1,QTableWidgetItem('Giải thích ngưỡng'))
            table.setItem(i,2,QTableWidgetItem('Xuất'))
        hh.addWidget(table)
        root.addWidget(chat,2); root.addWidget(history,1)

