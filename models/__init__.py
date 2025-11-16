"""
Models package - Data models (pure Python classes)
"""
from .user import User
from .customer import Customer
from .prediction_result import PredictionResult

__all__ = ['User', 'Customer', 'PredictionResult']
