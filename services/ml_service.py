"""
ML Service
Service giao tiếp với ML models và xử lý dự báo
"""
import sys
from pathlib import Path
from typing import Dict, Optional

# Add ml package to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.predictor import ModelPredictor
from ml.preprocess import preprocess_input
from models.prediction_result import PredictionResult


class MLService:
    """
    Service quản lý ML models và dự báo
    """
    
    def __init__(self, model_path: Optional[str] = None, model_name: str = 'XGBoost'):
        """
        Khởi tạo MLService
        
        Args:
            model_path: Đường dẫn tới file model .pkl
            model_name: Tên model (XGBoost/LightGBM/LogisticRegression)
        """
        import traceback
        print(f"🔥🔥🔥 MLService.__init__ CALLED with model_name={model_name} 🔥🔥🔥")
        print(f"🔥 Traceback:")
        for line in traceback.format_stack()[:-1]:
            if 'ui/' in line or 'PredictionTab' in line or 'MainWindow' in line or 'comparison' in line.lower():
                print(f"   {line.strip()}")
        
        self.model_name = model_name
        
        # Default model path nếu không cung cấp
        if model_path is None:
            models_dir = project_root / 'outputs' / 'models'
            if model_name == 'XGBoost':
                model_path = str(models_dir / 'xgb_model.pkl')
            elif model_name == 'LightGBM':
                model_path = str(models_dir / 'lgbm_model.pkl')
            elif model_name == 'LogisticRegression':
                model_path = str(models_dir / 'lr_cal_model.pkl')
            else:
                model_path = str(models_dir / 'xgb_model.pkl')
        
        self.model_path = model_path
        self.predictor = ModelPredictor(self.model_path)
        
        # Load model
        self.predictor.load_model()
    
    def predict_default_risk(self, input_dict: Dict) -> PredictionResult:
        """
        Dự báo rủi ro vỡ nợ
        
        Args:
            input_dict: Dict chứa 41 trường features (12 tháng lịch sử)
        
        Returns:
            Instance PredictionResult
        """
        try:
            # Preprocess input
            processed_input = preprocess_input(input_dict)
            
            # Predict
            label, probability = self.predictor.predict(processed_input)
            
            # Tạo PredictionResult
            result = PredictionResult(
                label=int(label),
                probability=float(probability),
                model_name=self.model_name,
                raw_outputs={'input': input_dict}
            )
            
            print(f"✓ Dự báo: {result}")
            return result
            
        except Exception as e:
            print(f"✗ Lỗi khi dự báo: {e}")
            # Trả về kết quả mặc định nếu lỗi
            return PredictionResult(
                label=0,
                probability=0.0,
                model_name=self.model_name,
                raw_outputs={'error': str(e)}
            )
    
    def get_model_info(self) -> Dict:
        """
        Lấy thông tin về model hiện tại
        
        Returns:
            Dict chứa thông tin model
        """
        return {
            'model_name': self.model_name,
            'model_path': self.model_path,
            'is_loaded': self.predictor.model is not None
        }
    
    def reload_model(self, new_model_path: Optional[str] = None):
        """
        Reload model từ file mới
        
        Args:
            new_model_path: Đường dẫn model mới (optional)
        """
        if new_model_path:
            self.model_path = new_model_path
        
        self.predictor = ModelPredictor(self.model_path)
        self.predictor.load_model()
        print(f"✓ Đã reload model: {self.model_path}")
