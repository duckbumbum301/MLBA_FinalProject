"""
Model Management Service
Service quản lý các mô hình Machine Learning
"""
import os
import time
import joblib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, 
    recall_score, f1_score, confusion_matrix
)

from database.connector import DatabaseConnector


class ModelManagementService:
    """
    Service quản lý training, switching, comparing models
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Khởi tạo Model Management Service
        
        Args:
            db_connector: Database connector
        """
        self.db = db_connector
        self.models_dir = Path("outputs/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách tất cả models từ database
        
        Returns:
            List of model info dicts
        """
        query = """
            SELECT id, model_name, model_type, algorithm, version,
                   auc_score, accuracy, precision_score, recall_score, f1_score,
                   is_active, training_time, trained_at, trained_by,
                   model_path, model_size_mb
            FROM model_registry
            ORDER BY auc_score DESC
        """
        
        results = self.db.fetch_all(query)
        
        models = []
        for row in results:
            models.append({
                'id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'algorithm': row[3],
                'version': row[4],
                'auc_score': float(row[5]) if row[5] else None,
                'accuracy': float(row[6]) if row[6] else None,
                'precision_score': float(row[7]) if row[7] else None,
                'recall_score': float(row[8]) if row[8] else None,
                'f1_score': float(row[9]) if row[9] else None,
                'is_active': bool(row[10]),
                'training_time': row[11],
                'trained_at': row[12],
                'trained_by': row[13],
                'model_path': row[14],
                'model_size_mb': float(row[15]) if row[15] else None
            })
        
        return models
    
    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """
        Lấy model đang active
        
        Returns:
            Model info dict hoặc None
        """
        query = """
            SELECT id, model_name, model_type, algorithm, model_path
            FROM model_registry
            WHERE is_active = 1
            LIMIT 1
        """
        
        result = self.db.fetch_one(query)
        
        if result:
            return {
                'id': result[0],
                'model_name': result[1],
                'model_type': result[2],
                'algorithm': result[3],
                'model_path': result[4]
            }
        return None
    
    def set_active_model(self, model_name: str, username: str) -> bool:
        """
        Set model làm active (chỉ 1 model active tại 1 thời điểm)
        
        Args:
            model_name: Tên model
            username: Username của admin thực hiện
        
        Returns:
            True nếu thành công
        """
        try:
            # Deactivate all models
            self.db.execute_query("UPDATE model_registry SET is_active = 0")
            
            # Activate selected model
            query = """
                UPDATE model_registry 
                SET is_active = 1, trained_by = %s
                WHERE model_name = %s
            """
            success = self.db.execute_query(query, (username, model_name))
            
            if success:
                print(f"✓ Set {model_name} as active model")
            
            return success
        
        except Exception as e:
            print(f"✗ Failed to set active model: {e}")
            return False
    
    def train_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        username: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Train một model cụ thể
        
        Args:
            model_name: Tên model ('LightGBM', 'CatBoost', etc.)
            X_train, y_train: Training data
            X_test, y_test: Test data
            username: Username của admin train
            progress_callback: Callback function(progress: int) để update progress
        
        Returns:
            Dict chứa metrics và model path
        """
        print(f"\n{'='*60}")
        print(f"TRAINING MODEL: {model_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Import model class
            model = self._create_model(model_name)
            
            if model is None:
                return {'success': False, 'error': f'Unknown model: {model_name}'}
            
            # Train
            if progress_callback:
                progress_callback(10)
            
            print(f"Training {model_name}...")
            model.fit(X_train, y_train)
            
            if progress_callback:
                progress_callback(60)
            
            # Evaluate
            print("Evaluating...")
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
            
            metrics = {
                'auc': roc_auc_score(y_test, y_pred_proba),
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0)
            }
            
            if progress_callback:
                progress_callback(80)
            
            # Save model
            model_filename = f"{model_name.lower().replace(' ', '_')}_model.pkl"
            model_path = self.models_dir / model_filename
            joblib.dump(model, model_path)
            
            model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            training_time = int(time.time() - start_time)
            
            if progress_callback:
                progress_callback(90)
            
            # Save to database
            self._save_model_to_db(
                model_name=model_name,
                algorithm=model_name,
                metrics=metrics,
                training_time=training_time,
                username=username,
                model_path=str(model_path),
                model_size_mb=model_size_mb
            )
            
            if progress_callback:
                progress_callback(100)
            
            print(f"\n✓ TRAINING COMPLETED!")
            print(f"  AUC: {metrics['auc']:.4f}")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  F1-Score: {metrics['f1']:.4f}")
            print(f"  Time: {training_time}s")
            print(f"  Saved to: {model_path}")
            
            return {
                'success': True,
                'model_name': model_name,
                'metrics': metrics,
                'training_time': training_time,
                'model_path': str(model_path),
                'model_size_mb': model_size_mb
            }
        
        except Exception as e:
            print(f"\n✗ TRAINING FAILED: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_model(self, model_name: str):
        """Tạo instance của model class"""
        if model_name == 'LightGBM':
            from lightgbm import LGBMClassifier
            return LGBMClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=7,
                num_leaves=31,
                random_state=42,
                verbose=-1
            )
        
        elif model_name == 'CatBoost':
            from catboost import CatBoostClassifier
            return CatBoostClassifier(
                iterations=500,
                learning_rate=0.03,
                depth=6,
                random_state=42,
                verbose=False
            )
        
        elif model_name == 'RandomForest':
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=10,
                random_state=42,
                n_jobs=-1
            )
        
        elif model_name == 'Neural Network':
            # Placeholder - cần implement riêng với TensorFlow/Keras
            print("⚠ Neural Network training not yet implemented")
            return None
        
        elif model_name == 'Voting':
            # Voting ensemble - cần base models đã train
            print("⚠ Voting Ensemble training requires base models")
            return None
        
        elif model_name == 'Stacking':
            # Stacking ensemble - cần base models đã train
            print("⚠ Stacking Ensemble training requires base models")
            return None
        
        else:
            return None
    
    def _save_model_to_db(
        self,
        model_name: str,
        algorithm: str,
        metrics: Dict[str, float],
        training_time: int,
        username: str,
        model_path: str,
        model_size_mb: float
    ):
        """Lưu hoặc update model info vào database"""
        query = """
            INSERT INTO model_registry 
            (model_name, model_type, algorithm, auc_score, accuracy, 
             precision_score, recall_score, f1_score, training_time, 
             trained_by, model_path, model_size_mb)
            VALUES (%s, 'Single', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                auc_score = VALUES(auc_score),
                accuracy = VALUES(accuracy),
                precision_score = VALUES(precision_score),
                recall_score = VALUES(recall_score),
                f1_score = VALUES(f1_score),
                training_time = VALUES(training_time),
                trained_at = CURRENT_TIMESTAMP,
                trained_by = VALUES(trained_by),
                model_path = VALUES(model_path),
                model_size_mb = VALUES(model_size_mb)
        """
        
        self.db.execute_query(query, (
            model_name, algorithm,
            metrics['auc'], metrics['accuracy'],
            metrics['precision'], metrics['recall'], metrics['f1'],
            training_time, username, model_path, model_size_mb
        ))
    
    def delete_model(self, model_name: str) -> bool:
        """
        Xóa model (file + database record)
        
        Args:
            model_name: Tên model
        
        Returns:
            True nếu thành công
        """
        try:
            # Get model path
            query = "SELECT model_path, is_active FROM model_registry WHERE model_name = %s"
            result = self.db.fetch_one(query, (model_name,))
            
            if not result:
                print(f"✗ Model not found: {model_name}")
                return False
            
            model_path, is_active = result
            
            # Không cho xóa active model
            if is_active:
                print(f"✗ Cannot delete active model: {model_name}")
                return False
            
            # Delete file
            if model_path and os.path.exists(model_path):
                os.remove(model_path)
                print(f"✓ Deleted file: {model_path}")
            
            # Delete from database
            self.db.execute_query("DELETE FROM model_registry WHERE model_name = %s", (model_name,))
            print(f"✓ Deleted from database: {model_name}")
            
            return True
        
        except Exception as e:
            print(f"✗ Failed to delete model: {e}")
            return False
    
    def load_model(self, model_name: str):
        """
        Load model từ file
        
        Args:
            model_name: Tên model
        
        Returns:
            Model object hoặc None
        """
        query = "SELECT model_path FROM model_registry WHERE model_name = %s"
        result = self.db.fetch_one(query, (model_name,))
        
        if not result or not result[0]:
            print(f"✗ Model not found in database: {model_name}")
            return None
        
        model_path = result[0]
        
        if not os.path.exists(model_path):
            print(f"✗ Model file not found: {model_path}")
            return None
        
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            return None
    
    def compare_models(
        self,
        model_names: List[str],
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Dict[str, float]]:
        """
        So sánh performance của nhiều models
        
        Args:
            model_names: List tên models
            X_test, y_test: Test data
        
        Returns:
            Dict {model_name: metrics_dict}
        """
        results = {}
        
        for model_name in model_names:
            model = self.load_model(model_name)
            
            if model is None:
                results[model_name] = {'error': 'Model not found'}
                continue
            
            try:
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
                
                results[model_name] = {
                    'auc': roc_auc_score(y_test, y_pred_proba),
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, zero_division=0),
                    'recall': recall_score(y_test, y_pred, zero_division=0),
                    'f1': f1_score(y_test, y_pred, zero_division=0)
                }
            
            except Exception as e:
                results[model_name] = {'error': str(e)}
        
        return results
