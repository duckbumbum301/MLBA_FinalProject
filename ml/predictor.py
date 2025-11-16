"""
Predictor Module
Load và sử dụng ML models đã train để dự báo
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional


class ModelPredictor:
    """
    Lớp quản lý việc load và predict bằng ML model
    """
    
    def __init__(self, model_path: str):
        """
        Khởi tạo Predictor
        
        Args:
            model_path: Đường dẫn tới file model .pkl
        """
        self.model_path = Path(model_path)
        self.model = None
    
    def load_model(self) -> bool:
        """
        Load model từ file .pkl
        
        Returns:
            True nếu load thành công, False nếu thất bại
        """
        try:
            if not self.model_path.exists():
                print(f"✗ Không tìm thấy model: {self.model_path}")
                return False
            
            self.model = joblib.load(self.model_path)
            print(f"✓ Đã load model: {self.model_path}")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi load model: {e}")
            return False
    
    def predict(self, X: pd.DataFrame) -> Tuple[int, float]:
        """
        Dự đoán nhãn và xác suất
        
        Args:
            X: DataFrame chứa features (1 hàng hoặc nhiều hàng)
        
        Returns:
            Tuple (label, probability) cho hàng đầu tiên
            - label: 0 hoặc 1
            - probability: xác suất vỡ nợ (class 1)
        
        Raises:
            ValueError: Nếu model chưa được load
        """
        if self.model is None:
            raise ValueError("Model chưa được load. Hãy gọi load_model() trước.")
        
        try:
            # Predict probability
            proba = self.model.predict_proba(X)
            
            # Lấy xác suất class 1 (vỡ nợ)
            prob_default = proba[0, 1]
            
            # Nhãn dự đoán (threshold 0.5)
            label = 1 if prob_default >= 0.5 else 0
            
            return label, prob_default
            
        except Exception as e:
            print(f"✗ Lỗi predict: {e}")
            raise
    
    def predict_batch(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Dự đoán cho nhiều mẫu cùng lúc
        
        Args:
            X: DataFrame chứa nhiều hàng
        
        Returns:
            Tuple (labels, probabilities)
            - labels: array nhãn dự đoán
            - probabilities: array xác suất vỡ nợ
        """
        if self.model is None:
            raise ValueError("Model chưa được load")
        
        try:
            proba = self.model.predict_proba(X)
            prob_defaults = proba[:, 1]
            labels = (prob_defaults >= 0.5).astype(int)
            
            return labels, prob_defaults
            
        except Exception as e:
            print(f"✗ Lỗi predict_batch: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """
        Lấy thông tin về model
        
        Returns:
            Dict chứa thông tin model
        """
        if self.model is None:
            return {'loaded': False, 'path': str(self.model_path)}
        
        model_type = type(self.model).__name__
        
        info = {
            'loaded': True,
            'path': str(self.model_path),
            'type': model_type
        }
        
        # Thêm thông tin đặc thù nếu có
        try:
            if hasattr(self.model, 'n_estimators'):
                info['n_estimators'] = self.model.n_estimators
            if hasattr(self.model, 'best_iteration_'):
                info['best_iteration'] = self.model.best_iteration_
        except:
            pass
        
        return info
