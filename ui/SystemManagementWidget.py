"""
System Management Widget
Tab quản lý hệ thống dành cho Admin - Phân tích chất lượng dữ liệu và phân cụm khách hàng
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QGroupBox, QMessageBox, QProgressDialog, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from typing import List, Dict, Any
import traceback

from models.user import User
from services.data_quality_service import DataQualityService
from database.connector import DatabaseConnector


class DataQualityWorker(QThread):
    """Worker thread để chạy data quality analysis"""
    finished = pyqtSignal(dict)  # {outliers: List[Dict], stats: Dict}
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, service: DataQualityService, method: str, contamination: float):
        super().__init__()
        self.service = service
        self.method = method
        self.contamination = contamination
    
    def run(self):
        try:
            self.progress.emit(30)
            result = self.service.detect_outliers(
                method=self.method,
                contamination=self.contamination
            )
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"{e}\n{traceback.format_exc()}")


class ClusteringWorker(QThread):
    """Worker thread để chạy clustering"""
    finished = pyqtSignal(dict)  # {clusters: List[Dict], visualization: str}
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, service: DataQualityService, algorithm: str, n_clusters: int):
        super().__init__()
        self.service = service
        self.algorithm = algorithm
        self.n_clusters = n_clusters
    
    def run(self):
        try:
            self.progress.emit(30)
            result = self.service.cluster_customers(
                algorithm=self.algorithm,
                n_clusters=self.n_clusters
            )
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"{e}\n{traceback.format_exc()}")


class SystemManagementWidget(QWidget):
    """
    Widget quản lý hệ thống
    - Phát hiện outliers (3 thuật toán)
    - Phân cụm khách hàng (K-Means, DBSCAN)
    - Xem thống kê chất lượng dữ liệu
    """
    
    def __init__(self, user: User, db_connector: DatabaseConnector):
        super().__init__()
        self.user = user
        self.db = db_connector
        self.data_quality_service = DataQualityService(db_connector)
        
        self.outlier_worker = None
        self.clustering_worker = None
        self.progress_dialog = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("🔧 QUẢN LÝ HỆ THỐNG")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Admin check
        if not self.user.is_admin():
            warning = QLabel("⚠️ Bạn không có quyền truy cập tab này")
            warning.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
            warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(warning)
            self.setLayout(layout)
            return
        
        # Outlier Detection Section
        outlier_group = self.create_outlier_section()
        layout.addWidget(outlier_group)
        
        # Clustering Section
        clustering_group = self.create_clustering_section()
        layout.addWidget(clustering_group)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Tên KH", "Risk Level", "Cluster", "Issues", "Actions"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.results_table)
        
        self.setLayout(layout)
    
    def create_outlier_section(self) -> QGroupBox:
        """Tạo section phát hiện outliers"""
        group = QGroupBox("🔍 Phát Hiện Dữ Liệu Bất Thường (Outliers)")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Method selector
        method_label = QLabel("Thuật toán:")
        self.outlier_method = QComboBox()
        self.outlier_method.addItems([
            "IsolationForest",
            "LocalOutlierFactor",
            "ZScore"
        ])
        self.outlier_method.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 150px;
            }
        """)
        
        # Contamination selector
        contamination_label = QLabel("Tỷ lệ outlier:")
        self.contamination_spin = QDoubleSpinBox()
        self.contamination_spin.setRange(0.01, 0.5)
        self.contamination_spin.setValue(0.05)
        self.contamination_spin.setSingleStep(0.01)
        self.contamination_spin.setSuffix(" (5%)")
        self.contamination_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        
        # Detect button
        detect_btn = QPushButton("🔍 Phát Hiện Outliers")
        detect_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        detect_btn.clicked.connect(self.detect_outliers)
        
        layout.addWidget(method_label)
        layout.addWidget(self.outlier_method)
        layout.addWidget(contamination_label)
        layout.addWidget(self.contamination_spin)
        layout.addWidget(detect_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_clustering_section(self) -> QGroupBox:
        """Tạo section phân cụm khách hàng"""
        group = QGroupBox("📊 Phân Cụm Khách Hàng (Customer Clustering)")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Algorithm selector
        algo_label = QLabel("Thuật toán:")
        self.clustering_algo = QComboBox()
        self.clustering_algo.addItems(["KMeans", "DBSCAN"])
        self.clustering_algo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 120px;
            }
        """)
        
        # Number of clusters
        n_clusters_label = QLabel("Số cụm:")
        self.n_clusters_spin = QSpinBox()
        self.n_clusters_spin.setRange(2, 10)
        self.n_clusters_spin.setValue(4)
        self.n_clusters_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 80px;
            }
        """)
        
        # Cluster button
        cluster_btn = QPushButton("📊 Phân Cụm")
        cluster_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        cluster_btn.clicked.connect(self.cluster_customers)
        
        layout.addWidget(algo_label)
        layout.addWidget(self.clustering_algo)
        layout.addWidget(n_clusters_label)
        layout.addWidget(self.n_clusters_spin)
        layout.addWidget(cluster_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def detect_outliers(self):
        """Phát hiện outliers"""
        method = self.outlier_method.currentText()
        contamination = self.contamination_spin.value()
        
        # Show progress dialog
        self.progress_dialog = QProgressDialog(
            f"Đang phát hiện outliers bằng {method}...",
            "Hủy",
            0, 100,
            self
        )
        self.progress_dialog.setWindowTitle("Phân Tích Dữ Liệu")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        
        # Start worker thread
        self.outlier_worker = DataQualityWorker(
            self.data_quality_service,
            method,
            contamination
        )
        self.outlier_worker.progress.connect(self.progress_dialog.setValue)
        self.outlier_worker.finished.connect(self.on_outlier_detection_finished)
        self.outlier_worker.error.connect(self.on_worker_error)
        self.outlier_worker.start()
    
    def cluster_customers(self):
        """Phân cụm khách hàng"""
        algorithm = self.clustering_algo.currentText()
        n_clusters = self.n_clusters_spin.value()
        
        # Show progress dialog
        self.progress_dialog = QProgressDialog(
            f"Đang phân cụm khách hàng bằng {algorithm}...",
            "Hủy",
            0, 100,
            self
        )
        self.progress_dialog.setWindowTitle("Phân Cụm Khách Hàng")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        
        # Start worker thread
        self.clustering_worker = ClusteringWorker(
            self.data_quality_service,
            algorithm,
            n_clusters
        )
        self.clustering_worker.progress.connect(self.progress_dialog.setValue)
        self.clustering_worker.finished.connect(self.on_clustering_finished)
        self.clustering_worker.error.connect(self.on_worker_error)
        self.clustering_worker.start()
    
    def on_outlier_detection_finished(self, result: Dict[str, Any]):
        """Xử lý kết quả phát hiện outliers"""
        self.progress_dialog.close()
        
        outliers = result.get('outliers', [])
        stats = result.get('stats', {})
        
        # Update table
        self.results_table.setRowCount(len(outliers))
        
        for row, outlier in enumerate(outliers):
            # ID
            id_item = QTableWidgetItem(str(outlier['customer_id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(f"Customer {outlier['customer_id']}")
            self.results_table.setItem(row, 1, name_item)
            
            # Risk Level
            risk_item = QTableWidgetItem("HIGH RISK")
            risk_item.setBackground(QColor("#e74c3c"))
            risk_item.setForeground(QColor("white"))
            risk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 2, risk_item)
            
            # Cluster
            cluster_item = QTableWidgetItem("-")
            cluster_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 3, cluster_item)
            
            # Issues
            issues = outlier.get('issues', [])
            issues_text = ", ".join(issues[:3])  # Show first 3 issues
            if len(issues) > 3:
                issues_text += "..."
            issues_item = QTableWidgetItem(issues_text)
            self.results_table.setItem(row, 4, issues_item)
            
            # Actions
            actions_item = QTableWidgetItem("🗑️ Xóa")
            actions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 5, actions_item)
        
        # Show summary
        n_outliers = stats.get('n_outliers', len(outliers))
        total = stats.get('total_customers', 0)
        method = stats.get('method', 'Unknown')
        
        QMessageBox.information(
            self,
            "Hoàn Thành",
            f"✓ Phát hiện {n_outliers}/{total} outliers bằng {method}\n\n"
            f"Kết quả đã được hiển thị trong bảng."
        )
    
    def on_clustering_finished(self, result: Dict[str, Any]):
        """Xử lý kết quả phân cụm"""
        self.progress_dialog.close()
        
        clusters = result.get('clusters', [])
        stats = result.get('stats', {})
        
        # Update table
        self.results_table.setRowCount(len(clusters))
        
        cluster_colors = {
            0: QColor("#3498db"),  # Blue
            1: QColor("#2ecc71"),  # Green
            2: QColor("#f39c12"),  # Orange
            3: QColor("#e74c3c"),  # Red
        }
        
        risk_levels = ["Low", "Medium", "High", "Critical"]
        
        for row, customer in enumerate(clusters):
            # ID
            id_item = QTableWidgetItem(str(customer['customer_id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(f"Customer {customer['customer_id']}")
            self.results_table.setItem(row, 1, name_item)
            
            # Risk Level
            cluster_id = customer['cluster']
            risk_level = risk_levels[min(cluster_id, 3)]
            risk_item = QTableWidgetItem(risk_level)
            risk_item.setBackground(cluster_colors.get(cluster_id, QColor("#95a5a6")))
            risk_item.setForeground(QColor("white"))
            risk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 2, risk_item)
            
            # Cluster
            cluster_item = QTableWidgetItem(f"Cluster {cluster_id}")
            cluster_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 3, cluster_item)
            
            # Issues
            issues_item = QTableWidgetItem("-")
            self.results_table.setItem(row, 4, issues_item)
            
            # Actions
            actions_item = QTableWidgetItem("📊 Chi tiết")
            actions_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 5, actions_item)
        
        # Show summary
        algorithm = stats.get('algorithm', 'Unknown')
        n_clusters = stats.get('n_clusters', 0)
        silhouette = stats.get('silhouette_score', 0)
        
        QMessageBox.information(
            self,
            "Hoàn Thành",
            f"✓ Phân cụm thành công bằng {algorithm}\n\n"
            f"Số cụm: {n_clusters}\n"
            f"Silhouette Score: {silhouette:.3f}\n\n"
            f"Kết quả đã được lưu vào database."
        )
    
    def on_worker_error(self, error_msg: str):
        """Xử lý lỗi từ worker thread"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(
            self,
            "Lỗi",
            f"❌ Có lỗi xảy ra:\n\n{error_msg}"
        )
