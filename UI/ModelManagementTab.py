from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit
from PyQt6.QtCore import QProcess
import subprocess, sys
from pathlib import Path

class ModelManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        header = QLabel('Quản Lý Mô Hình Machine Learning')
        layout.addWidget(header)
        self.table = QTableWidget(8, 6)
        self.table.setHorizontalHeaderLabels(['Active', 'Model Name', 'AUC', 'Accuracy', 'Trained', 'Actions'])
        models = [
            ('✅', 'XGBoost', '0.87', '82%', '2h ago', 'Details'),
            ('', 'Random Forest', '0.84', '79%', '2h ago', 'Active'),
            ('', 'LightGBM', '0.88', '83%', '-', 'Train'),
            ('', 'CatBoost', '-', '-', '-', 'Train'),
            ('', 'Neural Net', '-', '-', '-', 'Train'),
            ('', 'Voting', '0.89', '84%', '2h ago', 'Config'),
            ('', 'Stacking', '0.90', '85%', '2h ago', 'Config'),
            ('', 'Logistic', '0.77', '75%', '2h ago', 'Delete')
        ]
        for i, row in enumerate(models):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        btn_train = QPushButton('Train All Models')
        btn_train.clicked.connect(self.train_all)
        actions.addWidget(btn_train)
        actions.addWidget(QPushButton('Benchmark All'))
        actions.addWidget(QPushButton('Compare Selected'))
        actions.addStretch()
        layout.addLayout(actions)
        self.log = QTextEdit(); self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setLayout(layout)
        self.proc = None

    def train_all(self):
        root = Path(__file__).resolve().parents[1] / 'MLBA_FinalProject'
        script = str(root / 'ml' / 'train_models.py')
        python = sys.executable
        try:
            if self.proc:
                self.proc.kill()
            self.proc = QProcess(self)
            self.proc.setWorkingDirectory(str(root))
            self.proc.start(python, [script])
            self.proc.readyReadStandardOutput.connect(self._read_out)
            self.proc.readyReadStandardError.connect(self._read_err)
        except Exception:
            pass

    def _read_out(self):
        try:
            data = self.proc.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            self.log.append(data)
        except Exception:
            pass

    def _read_err(self):
        try:
            data = self.proc.readAllStandardError().data().decode('utf-8', errors='ignore')
            self.log.append(data)
        except Exception:
            pass
