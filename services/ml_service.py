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
        
        # Load optimal threshold from evaluation data if available
        self.threshold = self._load_optimal_threshold()
        self.overlay_config = self._load_overlay_config()
    
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
            _, probability = self.predictor.predict(processed_input)
            self.threshold = self._load_optimal_threshold()
            self.overlay_config = self._load_overlay_config()
            risk_score = float(probability)
            cfg = self.overlay_config or {}
            if bool(cfg.get('enabled', False)):
                alpha = float(cfg.get('alpha', 1.0))
                beta = float(cfg.get('beta', 0.0))
                feat = str(cfg.get('feature', 'NONE'))
                x = 0.0
                try:
                    if feat == 'AGE':
                        x = float(processed_input.get('AGE', 0)) / 100.0
                    elif feat == 'LIMIT_BAL':
                        x = float(processed_input.get('LIMIT_BAL', 0)) / 1000000.0
                    elif feat == 'PAY_0':
                        x = (float(processed_input.get('PAY_0', 0)) + 2.0) / 11.0
                except Exception:
                    x = 0.0
                x = max(0.0, min(1.0, x))
                risk_score = alpha * float(probability) + beta * x
                risk_score = max(0.0, min(1.0, risk_score))
            label = 1 if risk_score >= float(self.threshold) else 0
            
            # Tạo PredictionResult
            result = PredictionResult(
                label=int(label),
                probability=float(probability),
                model_name=self.model_name,
                raw_outputs={'input': input_dict, 'risk_score': float(risk_score), 'threshold': float(self.threshold), 'overlay': cfg}
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
            'is_loaded': self.predictor.model is not None,
            'threshold': self.threshold
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

    def _load_optimal_threshold(self) -> float:
        """
        Load optimal threshold từ outputs/evaluation/evaluation_data.npz
        Nếu không có, trả về 0.5
        """
        try:
            eval_path = project_root / 'outputs' / 'evaluation' / 'evaluation_data.npz'
            if not eval_path.exists():
                return 0.5
            import numpy as np
            data = np.load(eval_path, allow_pickle=True)
            best = data.get('best_thresholds', None)
            if best is None:
                return 0.5
            # best_thresholds được lưu là dict (object)
            thr_dict = best.item() if hasattr(best, 'item') else best
            return float(thr_dict.get(self.model_name, 0.5))
        except Exception:
            return 0.5

    def _load_overlay_config(self):
        try:
            eval_path = project_root / 'outputs' / 'evaluation' / 'evaluation_data.npz'
            if not eval_path.exists():
                return {'enabled': False}
            import numpy as np
            data = np.load(eval_path, allow_pickle=True)
            cfg = data.get('overlay_config', None)
            if cfg is None:
                return {'enabled': False}
            return cfg.item() if hasattr(cfg, 'item') else cfg
        except Exception:
            return {'enabled': False}
