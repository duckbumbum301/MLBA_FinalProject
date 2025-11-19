"""
Evaluation Module
Các hàm load dữ liệu đánh giá và vẽ biểu đồ cho Dashboard
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple, Optional
from matplotlib.figure import Figure
from sklearn.metrics import confusion_matrix


# Đường dẫn tới thư mục evaluation
EVAL_DIR = Path(__file__).parent.parent / 'outputs' / 'evaluation'


def load_evaluation_data() -> Dict:
    """
    Load dữ liệu evaluation đã lưu sẵn từ file .npz
    
    Returns:
        Dict chứa các dữ liệu evaluation:
        - feature_importance: dict {feature_name: importance_score}
        - confusion_matrix: dict {model_name: confusion_matrix}
        - roc_data: dict {model_name: (fpr, tpr, auc)}
        - risk_distribution: DataFrame
    """
    eval_file = EVAL_DIR / 'evaluation_data.npz'
    
    if not eval_file.exists():
        print(f"⚠ Không tìm thấy file evaluation: {eval_file}")
        print("⚠ Sử dụng dữ liệu demo mặc định")
        return load_demo_data()
    
    try:
        data = np.load(eval_file, allow_pickle=True)
        
        result = {
            'feature_importance': data.get('feature_importance', {}).item(),
            'confusion_matrices': data.get('confusion_matrices', {}).item(),
            'roc_data': data.get('roc_data', {}).item(),
            'y_test': data.get('y_test', np.array([])),
            'predictions': data.get('predictions', {}).item()
        }
        
        print(f"✓ Đã load evaluation data từ: {eval_file}")
        return result
        
    except Exception as e:
        print(f"✗ Lỗi load evaluation data: {e}")
        return load_demo_data()


def load_demo_data() -> Dict:
    """
    Tạo dữ liệu demo cho Dashboard khi chưa có evaluation data thực (41 features)
    
    Returns:
        Dict chứa demo data
    """
    # Feature importance demo (41 features, dựa theo notebook: PAY_0 là quan trọng nhất)
    # Top 20 features hiển thị trong chart
    feature_importance = {
        'PAY_0': 0.25,
        'PAY_2': 0.15,
        'LIMIT_BAL': 0.12,
        'PAY_3': 0.10,
        'BILL_AMT1': 0.08,
        'PAY_AMT1': 0.07,
        'AGE': 0.06,
        'PAY_4': 0.05,
        'PAY_5': 0.04,
        'PAY_6': 0.04,
        'PAY_7': 0.03,
        'BILL_AMT2': 0.02,
        'PAY_8': 0.02,
        'BILL_AMT3': 0.02,
        'PAY_9': 0.02,
        'PAY_AMT2': 0.02,
        'PAY_10': 0.01,
        'BILL_AMT4': 0.01,
        'PAY_11': 0.01,
        'PAY_12': 0.01,
        # Các features còn lại có importance thấp hơn
        'EDUCATION': 0.01,
        'SEX': 0.01,
        'MARRIAGE': 0.01
    }
    
    # Confusion matrix demo
    confusion_matrices = {
        'XGBoost': np.array([[3500, 200], [300, 1000]]),
        'LightGBM': np.array([[3450, 250], [320, 980]]),
        'LogisticRegression': np.array([[3400, 300], [400, 900]])
    }
    
    # ROC data demo
    fpr_demo = np.linspace(0, 1, 100)
    roc_data = {
        'XGBoost': (fpr_demo, 0.7 + 0.3 * fpr_demo**0.5, 0.82),
        'LightGBM': (fpr_demo, 0.65 + 0.35 * fpr_demo**0.5, 0.80),
        'LogisticRegression': (fpr_demo, 0.6 + 0.4 * fpr_demo**0.5, 0.75)
    }
    
    # Demo y_test và predictions
    y_test = np.array([0]*3700 + [1]*1300)  # Imbalanced như thực tế
    predictions = {
        'XGBoost': np.random.rand(5000) * 0.3 + (y_test * 0.5)
    }
    
    return {
        'feature_importance': feature_importance,
        'confusion_matrices': confusion_matrices,
        'roc_data': roc_data,
        'y_test': y_test,
        'predictions': predictions
    }


def plot_feature_importance(ax, feature_importance: Dict, top_n: int = 10) -> None:
    """
    Vẽ biểu đồ Feature Importance
    
    Args:
        ax: Matplotlib axes
        feature_importance: Dict {feature_name: importance}
        top_n: Số lượng features hiển thị
    """
    # Sort và lấy top N
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [f[0] for f in sorted_features]
    importance = [f[1] for f in sorted_features]
    
    # Vẽ horizontal bar chart
    colors_list = ['darkred' if f == 'PAY_0' else 'steelblue' for f in features]
    ax.barh(features, importance, color=colors_list)
    ax.set_xlabel('Importance Score', fontsize=10)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)


def plot_confusion_matrix(ax, cm: np.ndarray, model_name: str = 'XGBoost') -> None:
    """
    Vẽ biểu đồ Confusion Matrix
    
    Args:
        ax: Matplotlib axes
        cm: Confusion matrix (2x2 array)
        model_name: Tên model
    """
    # Vẽ heatmap with rotation=0 to avoid recursion
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, 
                cbar=False, square=True, linewidths=1, linecolor='black')
    
    ax.set_xlabel('Predicted Label', fontsize=10)
    ax.set_ylabel('True Label', fontsize=10)
    ax.set_xticklabels(['No Default (0)', 'Default (1)'], rotation=0)
    ax.set_yticklabels(['No Default (0)', 'Default (1)'], rotation=0)


def plot_roc_curves(ax, roc_data: Dict) -> None:
    """
    Vẽ biểu đồ ROC Curves cho nhiều models
    
    Args:
        ax: Matplotlib axes
        roc_data: Dict {model_name: (fpr, tpr, auc)}
    """
    colors = ['darkred', 'darkblue', 'darkgreen']
    
    for i, (model_name, data) in enumerate(roc_data.items()):
        fpr, tpr, auc = data
        color = colors[i % len(colors)]
        ax.plot(fpr, tpr, label=f'{model_name} (AUC={auc:.3f})', 
                color=color, linewidth=2)
    
    # Đường chéo (random classifier)
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random (AUC=0.500)')
    
    ax.set_xlabel('False Positive Rate', fontsize=10)
    ax.set_ylabel('True Positive Rate', fontsize=10)
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])


def plot_risk_distribution(ax, y_test: np.ndarray, predictions: Dict) -> None:
    """
    Vẽ biểu đồ phân phối rủi ro (Risk Distribution)
    Hiển thị tỷ lệ vỡ nợ theo nhóm xác suất dự đoán
    
    Args:
        ax: Matplotlib axes
        y_test: Array nhãn thực tế
        predictions: Dict {model_name: predicted_probabilities}
    """
    # Lấy predictions của model chính (XGBoost hoặc model đầu tiên)
    model_name = list(predictions.keys())[0] if predictions else 'XGBoost'
    probs = predictions.get(model_name, np.random.rand(len(y_test)))
    
    # Chia thành các bins xác suất
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bin_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    
    # Gán mỗi sample vào bin
    bin_indices = np.digitize(probs, bins) - 1
    bin_indices = np.clip(bin_indices, 0, len(bin_labels) - 1)
    
    # Tính tỷ lệ default thực tế trong mỗi bin
    default_rates = []
    counts = []
    
    for i in range(len(bin_labels)):
        mask = (bin_indices == i)
        if mask.sum() > 0:
            rate = y_test[mask].mean()
            count = mask.sum()
        else:
            rate = 0
            count = 0
        default_rates.append(rate * 100)  # Convert to percentage
        counts.append(count)
    
    # Vẽ bar chart
    x = np.arange(len(bin_labels))
    bars = ax.bar(x, default_rates, color='coral', edgecolor='black', linewidth=1)
    
    # Thêm số lượng samples trên mỗi bar
    for i, (bar, count) in enumerate(zip(bars, counts)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'n={count}', ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Predicted Probability Range', fontsize=10)
    ax.set_ylabel('Actual Default Rate (%)', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(bin_labels, rotation=0)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, 100])


def create_dashboard_figure() -> Tuple[Figure, np.ndarray]:
    """
    Tạo Figure với 4 subplots cho Dashboard (2x2 grid)
    
    Returns:
        Tuple (Figure, axes_array)
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Credit Risk Model Evaluation Dashboard', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    return fig, axes
