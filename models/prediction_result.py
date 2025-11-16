"""
Prediction Result Model
Model cho kết quả dự báo từ ML model
"""
from typing import Dict, Optional


class PredictionResult:
    """
    Lớp đại diện cho kết quả dự báo rủi ro
    """
    
    def __init__(
        self,
        label: int,
        probability: float,
        model_name: str,
        raw_outputs: Optional[Dict] = None
    ):
        """
        Khởi tạo PredictionResult
        
        Args:
            label: Nhãn dự đoán (0=không vỡ nợ, 1=vỡ nợ)
            probability: Xác suất vỡ nợ (0-1)
            model_name: Tên mô hình đã dùng
            raw_outputs: Output thô từ model (optional)
        """
        self.label = label
        self.probability = probability
        self.model_name = model_name
        self.raw_outputs = raw_outputs or {}
    
    def is_high_risk(self, threshold: float = 0.5) -> bool:
        """
        Kiểm tra có phải là nguy cơ cao không
        
        Args:
            threshold: Ngưỡng xác suất (mặc định 0.5)
        
        Returns:
            True nếu probability >= threshold
        """
        return self.probability >= threshold
    
    def get_risk_label(self, threshold: float = 0.5) -> str:
        """
        Lấy nhãn rủi ro dạng text tiếng Việt
        
        Args:
            threshold: Ngưỡng xác suất
        
        Returns:
            Chuỗi 'Nguy cơ cao' hoặc 'Nguy cơ thấp'
        """
        return "Nguy cơ cao" if self.is_high_risk(threshold) else "Nguy cơ thấp"
    
    def get_probability_percentage(self) -> str:
        """
        Lấy xác suất dạng phần trăm (string)
        
        Returns:
            Chuỗi dạng "87.5%"
        """
        return f"{self.probability * 100:.1f}%"
    
    def to_dict(self) -> Dict:
        """
        Chuyển thành dictionary
        
        Returns:
            Dict chứa thông tin prediction
        """
        return {
            'label': self.label,
            'probability': self.probability,
            'model_name': self.model_name,
            'raw_outputs': self.raw_outputs
        }
    
    def __repr__(self) -> str:
        return f"PredictionResult(label={self.label}, probability={self.probability:.4f}, model='{self.model_name}')"
    
    def __str__(self) -> str:
        return f"{self.get_risk_label()} ({self.get_probability_percentage()})"
