# Project Structure Documentation

## Overview

This document describes the architecture and structure of the Credit Risk Scoring System.

## Architecture

The project follows a **layered architecture** pattern:

```
┌─────────────────────────────────────┐
│         UI Layer (PyQt6)            │
│  LoginWindowEx, MainWindowEx,       │
│  PredictionTabWidget, Dashboard     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Services Layer                │
│  AuthService, QueryService,         │
│  MLService                          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Data Access Layer                │
│  DatabaseConnector, Models          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         MySQL Database              │
│  Tables: user, customers,           │
│  predictions_log                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       ML Layer (Separate)           │
│  Preprocess, Predictor, Evaluation  │
└─────────────────────────────────────┘
```

## Directory Structure Details

### `/config`

Configuration management.

- **database_config.py**: Database connection parameters
  - `DatabaseConfig` class with MySQL credentials

### `/database`

Database connectivity and SQL schemas.

- **connector.py**: `DatabaseConnector` class
  - `connect()`, `execute_query()`, `fetch_all()`, `fetch_one()`, `close()`
  - Uses parameterized queries (防 SQL injection)

- **credit_scoring/**: SQL scripts
  - `user.sql`: User accounts table
  - `customers.sql`: Customer data (41 features - 12 tháng lịch sử)
  - `predictions_log.sql`: Prediction history
  - `setup.sql`: Master setup script

### `/models`

Pure Python data models (no DB logic).

- **user.py**: `User` class
  - Fields: id, username, password_hash, role, created_at
  - Methods: `is_admin()`, `has_access_to_dashboard()`

- **customer.py**: `Customer` class
  - 41 fields (12 tháng lịch sử) - mở rộng từ UCI dataset
  - `to_dict()`, `from_dict()`

- **prediction_result.py**: `PredictionResult` class
  - Fields: label, probability, model_name
  - Methods: `is_high_risk()`, `get_risk_label()`

### `/services`

Business logic layer (intermediary between UI and Data).

- **auth_service.py**: `AuthService`
  - `login(username, password)` -> User | None
  - `hash_password()`, `verify_password()` (bcrypt)
  - `create_user()`, `change_password()`

- **query_service.py**: `QueryService`
  - `save_customer()`, `get_customer_by_id()`
  - `save_prediction_log()`, `get_recent_predictions()`

- **ml_service.py**: `MLService`
  - `predict_default_risk(input_dict)` -> PredictionResult
  - Load model từ .pkl file
  - Interface giữa UI và ML models

### `/ml`

Machine Learning utilities.

- **preprocess.py**
  - `preprocess_input(input_dict)` -> DataFrame
  - Data cleaning: EDUCATION/MARRIAGE mapping, PAY_* clipping

- **predictor.py**: `ModelPredictor`
  - `load_model()`, `predict(X)` -> (label, probability)
  - Supports batch prediction

- **evaluation.py**
  - `load_evaluation_data()` -> Dict
  - Plotting functions: `plot_feature_importance()`, `plot_confusion_matrix()`, etc.

- **train_models.py** ⚠️ CRITICAL
  - Training pipeline: Load data → Train models → Save .pkl + evaluation data
  - Must run before first app launch

### `/ui`

PyQt6 user interface.

**Qt Designer Files (.ui)**:
- `LoginWindow.ui`, `MainWindow.ui`

**Generated Python (.py)**:
- `LoginWindow.py`, `MainWindow.py`

**Extended Logic Classes**:
- **LoginWindowEx.py**
  - Signal: `login_successful(User)`
  - Connect DB → AuthService → Emit user

- **MainWindowEx.py**
  - Manage tabs, role-based permissions
  - Signal: `logout_signal()`

- **PredictionTabWidget.py**
  - 23 input fields (3 groups: Personal, Payment History, Billing)
  - Result display with color-coded risk
  - Save to DB option

- **DashboardTabWidget.py**
  - 4 matplotlib canvases (2x2 grid)
  - Refresh button

### `/tests`

Application entry point.

- **test_app.py**
  - `CreditRiskApp` controller
  - Flow: Login → MainWindow → Logout → Login
  - Main function: `python -m tests.test_app`

### `/outputs`

Generated files (ignored by git).

- **/models**: `.pkl` files (xgb_model.pkl, lgbm_model.pkl, lr_cal_model.pkl)
- **/charts**: PNG exports
- **/evaluation**: `evaluation_data.npz`

## Data Flow

### Login Flow

```
User input (username, password)
    ↓
LoginWindowEx.handle_login()
    ↓
DatabaseConnector.connect()
    ↓
AuthService.login(username, password)
    ↓
    - fetch user from DB
    - verify password (bcrypt)
    ↓
    [SUCCESS] → emit login_successful(User)
    ↓
CreditRiskApp.on_login_successful(user)
    ↓
MainWindowEx(user)
```

### Prediction Flow

```
User fills 23 fields
    ↓
PredictionTabWidget.on_predict_clicked()
    ↓
collect_input() → Dict
    ↓
MLService.predict_default_risk(input_dict)
    ↓
    ml.preprocess.preprocess_input()
    ↓
    ModelPredictor.predict()
    ↓
    [Model loaded from .pkl]
    ↓
    Return (label, probability)
    ↓
PredictionResult object
    ↓
display_result() → Update UI
    ↓
[Optional] save_prediction_to_db()
```

## Role-Based Access Control

Implemented in `MainWindowEx.setup_role_permissions()`:

| Role | Prediction Tab | Dashboard Tab |
|------|----------------|---------------|
| Admin | ✅ | ✅ |
| Technical | ✅ | ✅ |
| Secretary | ✅ | ❌ |

Logic: Dynamically remove tabs based on user role.

## Security

- **Password Hashing**: bcrypt (cost factor 12)
- **SQL Injection Prevention**: Parameterized queries (`cursor.execute(query, params)`)
- **Session Management**: User object passed between windows
- **Database Credentials**: Stored in `DatabaseConfig` (consider .env for production)

## Model Training Pipeline

Located in `ml/train_models.py`:

1. **Load Data**: `UCI_Credit_Card.csv`
2. **Preprocess**: 
   - EDUCATION/MARRIAGE mapping
   - PAY_* clipping
   - Split 70/15/15 (Train/Valid/Test)
3. **Train Models**:
   - XGBoost
   - LightGBM
   - Logistic Regression (Elastic Net + Isotonic Calibration)
4. **Evaluate**: Compute metrics, ROC, confusion matrix
5. **Save**:
   - Models → `outputs/models/*.pkl`
   - Evaluation data → `outputs/evaluation/evaluation_data.npz`

## Database Schema

### Table: `user`

```sql
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Technical', 'Secretary') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `customers`

23 fields matching UCI dataset + metadata (customer_name, customer_id_card).

### Table: `predictions_log`

```sql
CREATE TABLE predictions_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    model_name VARCHAR(50) NOT NULL,
    predicted_label TINYINT NOT NULL,
    probability DECIMAL(5,4) NOT NULL,
    raw_input_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

## Dependencies

See `requirements.txt`:

- PyQt6: GUI framework
- mysql-connector-python: MySQL driver
- scikit-learn: ML base library
- lightgbm, xgboost: Boosting models
- matplotlib, seaborn: Plotting
- bcrypt: Password hashing
- pandas, numpy: Data processing
- joblib: Model serialization

## Extension Points

To add new features:

1. **New Model**: 
   - Train in `train_models.py`
   - Save as `.pkl`
   - Update `MLService` to support model selection

2. **New Tab**:
   - Create `NewTabWidget.py`
   - Add to `MainWindowEx.setup_tabs()`
   - Update role permissions

3. **New User Role**:
   - Update ENUM in `user.sql`
   - Update `setup_role_permissions()` in MainWindowEx

4. **Export Feature**:
   - Add in `services/export_service.py`
   - Call from UI button

---

**Last Updated**: November 16, 2025
