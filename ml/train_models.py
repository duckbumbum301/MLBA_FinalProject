"""
Train Models Script
Script để train các ML models (LightGBM, XGBoost, Logistic Regression) 
và lưu models + evaluation data

Chạy script này trước khi sử dụng ứng dụng:
    python ml/train_models.py
"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, roc_curve, roc_auc_score, 
    average_precision_score, accuracy_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV

import lightgbm as lgb
import xgboost as xgb

try:
    from catboost import CatBoostClassifier
    HAVE_CATBOOST = True
except ImportError:
    HAVE_CATBOOST = False
    print("⚠ CatBoost not available, will skip")


# ========================================
# Paths
# ========================================
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / 'UCI_Credit_Card_12months.csv'  # Updated to 12-month dataset
MODELS_DIR = ROOT / 'outputs' / 'models'
EVAL_DIR = ROOT / 'outputs' / 'evaluation'

MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

TARGET = 'default.payment.next.month'
ID_COL = 'ID'
SEED = 42


# ========================================
# 1. Load và Preprocess Data
# ========================================
def load_and_preprocess():
    """Load và preprocess data theo logic notebook"""
    print("\n" + "="*60)
    print("STEP 1: LOAD & PREPROCESS DATA")
    print("="*60)
    
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file data: {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    print(f"✓ Loaded data: {df.shape}")
    
    # Preprocess theo notebook
    df['EDUCATION'] = df['EDUCATION'].replace({0:4, 4:4, 5:4, 6:4})
    df['MARRIAGE'] = df['MARRIAGE'].replace({0:3})
    
    # Clip PAY_* for all 12 months
    pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
                'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12']
    for c in pay_cols:
        if c in df.columns:
            df[c] = df[c].clip(-2, 9)
    
    # Separate features and target
    X = df.drop(columns=[TARGET, ID_COL] if ID_COL in df.columns else [TARGET])
    y = df[TARGET].astype(int)
    
    print(f"✓ Features: {X.shape[1]} columns")
    print(f"✓ Target distribution: {y.value_counts().to_dict()}")
    
    # Split 70/15/15
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=SEED
    )
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_temp, y_temp, test_size=0.17647, stratify=y_temp, random_state=SEED
    )
    
    print(f"✓ Train: {X_train.shape}, Valid: {X_valid.shape}, Test: {X_test.shape}")
    
    return X_train, X_valid, X_test, y_train, y_valid, y_test


# ========================================
# 2. Train XGBoost
# ========================================
def train_xgboost(X_train, X_valid, X_test, y_train, y_valid, y_test):
    """Train XGBoost model"""
    print("\n" + "="*60)
    print("STEP 2: TRAIN XGBOOST")
    print("="*60)
    
    pos = int(y_train.sum())
    neg = len(y_train) - pos
    scale_pos_weight = neg / max(pos, 1)
    
    xgb_model = xgb.XGBClassifier(
        objective='binary:logistic',
        learning_rate=0.05,
        n_estimators=1000,
        max_depth=6,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=SEED,
        n_jobs=-1,
        eval_metric='auc'
    )
    
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        verbose=False
    )
    
    # Evaluate
    y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    acc = accuracy_score(y_test, (y_pred_proba >= 0.5).astype(int))
    
    print(f"✓ XGBoost - Test AUC: {auc:.4f}, Accuracy: {acc:.4f}")
    
    # Save
    model_path = MODELS_DIR / 'xgb_model.pkl'
    joblib.dump(xgb_model, model_path)
    print(f"✓ Saved: {model_path}")
    
    # Feature importance
    feat_imp = dict(zip(X_train.columns, xgb_model.feature_importances_))
    
    return xgb_model, y_pred_proba, feat_imp


# ========================================
# 3. Train LightGBM
# ========================================
def train_lightgbm(X_train, X_valid, X_test, y_train, y_valid, y_test):
    """Train LightGBM model"""
    print("\n" + "="*60)
    print("STEP 3: TRAIN LIGHTGBM")
    print("="*60)
    
    pos = int(y_train.sum())
    neg = len(y_train) - pos
    scale_pos_weight = neg / max(pos, 1)
    
    lgb_model = lgb.LGBMClassifier(
        objective='binary',
        learning_rate=0.05,
        n_estimators=1000,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=SEED,
        n_jobs=-1,
        metric='None'
    )
    
    lgb_model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        eval_metric='auc',
        callbacks=[lgb.early_stopping(stopping_rounds=100, verbose=False)]
    )
    
    # Evaluate
    y_pred_proba = lgb_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    acc = accuracy_score(y_test, (y_pred_proba >= 0.5).astype(int))
    
    print(f"✓ LightGBM - Test AUC: {auc:.4f}, Accuracy: {acc:.4f}")
    
    # Save
    model_path = MODELS_DIR / 'lgbm_model.pkl'
    joblib.dump(lgb_model, model_path)
    print(f"✓ Saved: {model_path}")
    
    return lgb_model, y_pred_proba


# ========================================
# 4. Train Logistic Regression (Calibrated)
# ========================================
def train_logistic(X_train, X_valid, X_test, y_train, y_valid, y_test):
    """Train Logistic Regression with Elastic Net"""
    print("\n" + "="*60)
    print("STEP 4: TRAIN LOGISTIC REGRESSION")
    print("="*60)
    
    categorical = ['SEX', 'EDUCATION', 'MARRIAGE']
    numeric = [c for c in X_train.columns if c not in categorical]
    
    preprocess = ColumnTransformer([
        ("num", StandardScaler(with_mean=False), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ], remainder="drop")
    
    lr_pipe = Pipeline([
        ("prep", preprocess),
        ("clf", LogisticRegression(
            solver="saga",
            penalty="elasticnet",
            l1_ratio=1.0,
            C=0.01,
            max_iter=5000,
            class_weight="balanced",
            n_jobs=-1,
            random_state=SEED
        ))
    ])
    
    lr_pipe.fit(X_train, y_train)
    
    # Calibrate
    lr_cal = CalibratedClassifierCV(lr_pipe, method="isotonic", cv="prefit")
    lr_cal.fit(X_valid, y_valid)
    
    # Evaluate
    y_pred_proba = lr_cal.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    acc = accuracy_score(y_test, (y_pred_proba >= 0.5).astype(int))
    
    print(f"✓ Logistic (calibrated) - Test AUC: {auc:.4f}, Accuracy: {acc:.4f}")
    
    # Save
    model_path = MODELS_DIR / 'lr_cal_model.pkl'
    joblib.dump(lr_cal, model_path)
    print(f"✓ Saved: {model_path}")
    
    return lr_cal, y_pred_proba


# ========================================
# 5. Save Evaluation Data
# ========================================
def save_evaluation_data(
    X_test, y_test,
    xgb_pred, lgb_pred, lr_pred,
    xgb_model, feat_imp
):
    """Save evaluation data for Dashboard"""
    print("\n" + "="*60)
    print("STEP 5: SAVE EVALUATION DATA")
    print("="*60)
    
    # Confusion matrices
    cm_xgb = confusion_matrix(y_test, (xgb_pred >= 0.5).astype(int))
    cm_lgb = confusion_matrix(y_test, (lgb_pred >= 0.5).astype(int))
    cm_lr = confusion_matrix(y_test, (lr_pred >= 0.5).astype(int))
    
    confusion_matrices = {
        'XGBoost': cm_xgb,
        'LightGBM': cm_lgb,
        'LogisticRegression': cm_lr
    }
    
    # ROC data
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb_pred)
    fpr_lgb, tpr_lgb, _ = roc_curve(y_test, lgb_pred)
    fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_pred)
    
    auc_xgb = roc_auc_score(y_test, xgb_pred)
    auc_lgb = roc_auc_score(y_test, lgb_pred)
    auc_lr = roc_auc_score(y_test, lr_pred)
    
    roc_data = {
        'XGBoost': (fpr_xgb, tpr_xgb, auc_xgb),
        'LightGBM': (fpr_lgb, tpr_lgb, auc_lgb),
        'LogisticRegression': (fpr_lr, tpr_lr, auc_lr)
    }
    
    # Predictions dict
    predictions = {
        'XGBoost': xgb_pred,
        'LightGBM': lgb_pred,
        'LogisticRegression': lr_pred
    }
    
    # Save to .npz
    eval_file = EVAL_DIR / 'evaluation_data.npz'
    np.savez(
        eval_file,
        feature_importance=feat_imp,
        confusion_matrices=confusion_matrices,
        roc_data=roc_data,
        y_test=y_test,
        predictions=predictions
    )
    
    print(f"✓ Saved evaluation data: {eval_file}")


# ========================================
# Main
# ========================================
def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("CREDIT RISK MODEL TRAINING PIPELINE")
    print("="*60)
    
    # Load data
    X_train, X_valid, X_test, y_train, y_valid, y_test = load_and_preprocess()
    
    # Train models
    xgb_model, xgb_pred, feat_imp = train_xgboost(X_train, X_valid, X_test, y_train, y_valid, y_test)
    lgb_model, lgb_pred = train_lightgbm(X_train, X_valid, X_test, y_train, y_valid, y_test)
    lr_model, lr_pred = train_logistic(X_train, X_valid, X_test, y_train, y_valid, y_test)
    
    # Save evaluation data
    save_evaluation_data(
        X_test, y_test,
        xgb_pred, lgb_pred, lr_pred,
        xgb_model, feat_imp
    )
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nModels saved to: {MODELS_DIR}")
    print(f"Evaluation data saved to: {EVAL_DIR}")
    print("\nBạn có thể chạy ứng dụng PyQt6 bây giờ:")
    print("    python -m tests.test_app")


if __name__ == '__main__':
    main()
