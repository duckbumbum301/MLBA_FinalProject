from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem

class CopilotPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        root = QHBoxLayout(self)
        chat = QFrame(); chat.setObjectName('Card'); ch = QVBoxLayout(chat)
        ch.addWidget(QLabel('AI Risk Copilot'))
        self.input = QTextEdit(); self.input.setPlaceholderText('Ask: Explain model, threshold, summarize predictions...')
        actions = QHBoxLayout(); actions.addWidget(QPushButton('Explain model')); actions.addWidget(QPushButton('Explain threshold')); actions.addWidget(QPushButton('Summarize 100 predictions'))
        ch.addWidget(self.input); ch.addLayout(actions)
        history = QFrame(); history.setObjectName('Card'); hh = QVBoxLayout(history)
        hh.addWidget(QLabel('Chat History'))
        table = QTableWidget(5,3); table.setHorizontalHeaderLabels(['ts','prompt','action'])
        for i in range(5):
            table.setItem(i,0,QTableWidgetItem('10:20'))
            table.setItem(i,1,QTableWidgetItem('Explain threshold'))
            table.setItem(i,2,QTableWidgetItem('Export'))
        hh.addWidget(table)
        root.addWidget(chat,2); root.addWidget(history,1)

