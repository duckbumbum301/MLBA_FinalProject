"""
ML package - Machine Learning utilities
"""
from .preprocess import preprocess_input
from .predictor import ModelPredictor

# Avoid hard dependency on sklearn at import time
try:
    from .evaluation import (
        load_evaluation_data,
        plot_feature_importance,
        plot_confusion_matrix,
        plot_roc_curves,
        plot_risk_distribution,
    )
    _HAVE_EVAL = True
except Exception:
    _HAVE_EVAL = False

__all__ = ['preprocess_input', 'ModelPredictor']
if _HAVE_EVAL:
    __all__ += [
        'load_evaluation_data',
        'plot_feature_importance',
        'plot_confusion_matrix',
        'plot_roc_curves',
        'plot_risk_distribution',
    ]
