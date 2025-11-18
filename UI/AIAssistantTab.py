from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox

class AIAssistantTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        header = QLabel('AI Trợ Lý')
        layout.addWidget(header)
        actions = QComboBox()
        actions.addItems([
            'Giải thích kết quả vừa dự báo',
            'So sánh với khách hàng tương tự',
            'Đề xuất hành động tiếp theo',
            'Tóm tắt 5 predictions gần nhất'
        ])
        layout.addWidget(actions)
        input_row = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText('Câu hỏi của bạn')
        self.btn_send = QPushButton('Gửi')
        input_row.addWidget(self.input_line)
        input_row.addWidget(self.btn_send)
        layout.addLayout(input_row)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)
        self.setLayout(layout)
