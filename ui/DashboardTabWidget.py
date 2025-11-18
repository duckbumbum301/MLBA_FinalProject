"""
DashboardTabWidget
Tab Dashboard với 4 biểu đồ đánh giá mô hình ML
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.evaluation import (
    load_evaluation_data,
    plot_feature_importance,
    plot_confusion_matrix,
    plot_roc_curves,
    plot_risk_distribution
)


class MatplotlibCanvas(FigureCanvas):
    """Canvas cho matplotlib plot trong PyQt6"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


class DashboardTabWidget(QWidget):
    """
    Widget cho Tab Dashboard
    Hiển thị 4 biểu đồ trong layout 2x2:
    - Feature Importance
    - Confusion Matrix
    - ROC Curves
    - Risk Distribution
    """
    
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.eval_data = None
        self.setup_ui()
        self.load_and_plot_data()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        main_layout = QVBoxLayout()
        
        # Refresh button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btnRefresh = QPushButton("🔄 Refresh Dashboard")
        self.btnRefresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnRefresh.clicked.connect(self.refresh_dashboard)
        button_layout.addWidget(self.btnRefresh)
        
        main_layout.addLayout(button_layout)
        
        # Grid layout 2x2 cho 4 biểu đồ
        grid_layout = QGridLayout()
        
        # Canvas 1: Feature Importance (top-left)
        self.canvas_feature_importance = MatplotlibCanvas(self, width=7, height=5)
        grid_layout.addWidget(self.canvas_feature_importance, 0, 0)
        
        # Canvas 2: Confusion Matrix (top-right)
        self.canvas_confusion_matrix = MatplotlibCanvas(self, width=7, height=5)
        grid_layout.addWidget(self.canvas_confusion_matrix, 0, 1)
        
        # Canvas 3: ROC Curves (bottom-left)
        self.canvas_roc = MatplotlibCanvas(self, width=7, height=5)
        grid_layout.addWidget(self.canvas_roc, 1, 0)
        
        # Canvas 4: Risk Distribution (bottom-right)
        self.canvas_risk_dist = MatplotlibCanvas(self, width=7, height=5)
        grid_layout.addWidget(self.canvas_risk_dist, 1, 1)
        
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)
    
    def load_and_plot_data(self):
        """Load evaluation data và vẽ tất cả biểu đồ"""
        try:
            # Load data
            self.eval_data = load_evaluation_data()
            
            # Plot từng biểu đồ
            self.plot_feature_importance_chart()
            self.plot_confusion_matrix_chart()
            self.plot_roc_curves_chart()
            self.plot_risk_distribution_chart()
            
            print("✓ Dashboard loaded successfully")
        
        except Exception as e:
            print(f"⚠ Lỗi load dashboard: {e}")
    
    def plot_feature_importance_chart(self):
        """Vẽ biểu đồ Feature Importance"""
        try:
            ax = self.canvas_feature_importance.axes
            ax.clear()
            
            feature_importance = self.eval_data.get('feature_importance', {})
            plot_feature_importance(ax, feature_importance, top_n=10)
            
            self.canvas_feature_importance.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Feature Importance: {e}")
    
    def plot_confusion_matrix_chart(self):
        """Vẽ biểu đồ Confusion Matrix"""
        try:
            ax = self.canvas_confusion_matrix.axes
            ax.clear()
            
            confusion_matrices = self.eval_data.get('confusion_matrices', {})
            # Lấy confusion matrix của XGBoost (model chính)
            cm = confusion_matrices.get('XGBoost')
            
            if cm is not None:
                plot_confusion_matrix(ax, cm, model_name='XGBoost')
            else:
                ax.text(0.5, 0.5, 'No data available', 
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_confusion_matrix.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Confusion Matrix: {e}")
    
    def plot_roc_curves_chart(self):
        """Vẽ biểu đồ ROC Curves"""
        try:
            ax = self.canvas_roc.axes
            ax.clear()
            
            roc_data = self.eval_data.get('roc_data', {})
            
            if roc_data:
                plot_roc_curves(ax, roc_data)
            else:
                ax.text(0.5, 0.5, 'No data available',
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_roc.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ ROC Curves: {e}")
    
    def plot_risk_distribution_chart(self):
        """Vẽ biểu đồ Risk Distribution"""
        try:
            ax = self.canvas_risk_dist.axes
            ax.clear()
            
            y_test = self.eval_data.get('y_test')
            predictions = self.eval_data.get('predictions', {})
            
            if y_test is not None and len(y_test) > 0 and predictions:
                plot_risk_distribution(ax, y_test, predictions)
            else:
                ax.text(0.5, 0.5, 'No data available',
                       ha='center', va='center', transform=ax.transAxes)
            
            self.canvas_risk_dist.draw()
        
        except Exception as e:
            print(f"⚠ Lỗi vẽ Risk Distribution: {e}")
    
    def refresh_dashboard(self):
        """Refresh toàn bộ dashboard"""
        print("🔄 Refreshing dashboard...")
        self.load_and_plot_data()
