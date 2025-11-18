from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from pathlib import Path

class SystemManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        section1 = QVBoxLayout()
        section1.addWidget(QLabel('Phát hiện dữ liệu bất thường'))
        row1 = QHBoxLayout()
        method = QComboBox()
        method.addItems(['Isolation Forest'])
        threshold = QSpinBox()
        threshold.setRange(0, 100)
        threshold.setValue(5)
        btn_scan = QPushButton('Scan Database')
        row1.addWidget(QLabel('Method:'))
        row1.addWidget(method)
        row1.addWidget(QLabel('Threshold:'))
        row1.addWidget(threshold)
        row1.addWidget(btn_scan)
        section1.addLayout(row1)
        self.table1 = QTableWidget(0, 5)
        self.table1.setHorizontalHeaderLabels(['☑', 'Cust ID', 'Score', 'Issue', 'Actions'])
        section1.addWidget(self.table1)
        row2 = QHBoxLayout()
        row2.addWidget(QPushButton('Delete Selected'))
        row2.addWidget(QPushButton('Export Outliers'))
        section1.addLayout(row2)
        layout.addLayout(section1)
        section2 = QVBoxLayout()
        section2.addWidget(QLabel('Phân cụm khách hàng'))
        row3 = QHBoxLayout()
        algo = QComboBox()
        algo.addItems(['K-Means'])
        self.clusters = QSpinBox()
        self.clusters.setRange(2, 10)
        self.clusters.setValue(4)
        row3.addWidget(QLabel('Algorithm:'))
        row3.addWidget(algo)
        row3.addWidget(QLabel('Clusters:'))
        row3.addWidget(self.clusters)
        btn_run = QPushButton('Run')
        btn_scan.clicked.connect(lambda: self.run_outlier_scan(threshold.value()))
        btn_run.clicked.connect(self.run_kmeans)
        row3.addWidget(btn_run)
        section2.addLayout(row3)
        self.cluster_canvas = FigureCanvas(Figure(figsize=(5,3)))
        layout.addWidget(self.cluster_canvas)
        layout.addLayout(section2)
        self.setLayout(layout)

    def load_dataset(self) -> pd.DataFrame:
        root = Path(__file__).resolve().parents[1] / 'MLBA_FinalProject'
        csv = root / 'UCI_Credit_Card.csv'
        if csv.exists():
            try:
                return pd.read_csv(csv)
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()

    def run_outlier_scan(self, threshold_percent: int):
        df = self.load_dataset()
        if df.empty:
            return
        try:
            from sklearn.ensemble import IsolationForest
        except Exception:
            return
        cols = [c for c in df.columns if c.startswith('BILL_AMT') or c.startswith('PAY_AMT')]
        X = df[cols].fillna(0).values
        iso = IsolationForest(contamination=max(min(threshold_percent/100.0,0.4),0.01), random_state=42)
        scores = -iso.fit_predict(X)
        probs = iso.decision_function(X)
        idx = probs.argsort()[-150:][::-1]
        self.table1.setRowCount(len(idx))
        for i, j in enumerate(idx):
            self.table1.setItem(i, 0, QTableWidgetItem('☑'))
            self.table1.setItem(i, 1, QTableWidgetItem(str(df.iloc[j]['ID']) if 'ID' in df.columns else str(j)))
            self.table1.setItem(i, 2, QTableWidgetItem(f"{probs[j]:.2f}"))
            self.table1.setItem(i, 3, QTableWidgetItem('Outlier'))
            self.table1.setItem(i, 4, QTableWidgetItem('Edit/Delete'))

    def run_kmeans(self):
        df = self.load_dataset()
        if df.empty:
            return
        try:
            from sklearn.cluster import KMeans
        except Exception:
            return
        cols = ['LIMIT_BAL','AGE'] + [c for c in df.columns if c.startswith('PAY_')][:4]
        X = df[cols].fillna(0).values
        k = int(self.clusters.value())
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(X)
        labels = km.labels_
        counts = pd.Series(labels).value_counts().sort_index()
        ax = self.cluster_canvas.figure.subplots()
        ax.clear()
        ax.bar(counts.index.astype(str), counts.values, color='#9b59b6')
        ax.set_title('Phân bổ khách hàng theo cụm')
        ax.set_xlabel('Cụm')
        ax.set_ylabel('Số lượng')
        self.cluster_canvas.draw()
