# Chapter 3. System Architecture

This chapter provides a comprehensive overview of the system architecture, including the database schema, backend services, user interface components, and role-based access control mechanisms.

## 3.1. Database Schema

The Credit Risk Scoring System uses MySQL 8.x with UTF8MB4 encoding. The database consists of 7 core tables that support the entire application lifecycle.

### 3.1.1. User Table

**Purpose:** Authentication and authorization with role-based access control.

**Table 3.1: User table structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each user |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| role | ENUM('User','Admin') | NOT NULL | User role (User or Admin) |
| full_name | VARCHAR(100) | NULL | Full name of user |
| email | VARCHAR(100) | NULL | Email address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| last_login | DATETIME | NULL | Last successful login |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |

**SQL Creation Script:**
```sql
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('User', 'Admin') NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Sample Users:**
- `babyshark` (User role, password: `123`)
- `fathershark` (Admin role, password: `123`)
- `momshark` (User role, password: `123`)

### 3.1.2. Customers Table

**Purpose:** Store customer demographic and credit history data (41 features from 12-month expansion).

**Key Features:**
- 5 demographic features: LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE
- 12 payment status features: PAY_1 to PAY_12
- 12 bill amount features: BILL_AMT1 to BILL_AMT12
- 12 payment amount features: PAY_AMT1 to PAY_AMT12

**Table 3.2: Customers table structure (sample columns)**

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| customer_id | INT PRIMARY KEY | Unique customer identifier |
| LIMIT_BAL | INT | Credit limit (NT dollar) |
| SEX | INT | Gender (1=male, 2=female) |
| EDUCATION | INT | Education level |
| MARRIAGE | INT | Marital status |
| AGE | INT | Age in years |
| PAY_1 to PAY_12 | INT | Payment status for each month |
| BILL_AMT1 to BILL_AMT12 | INT | Bill statement amount |
| PAY_AMT1 to PAY_AMT12 | INT | Payment amount |
| default_payment_next_month | INT | Target variable (0=no, 1=yes) |

### 3.1.3. Predictions Log Table

**Purpose:** Track all predictions made by the system with full audit trail.

**Table 3.3: Predictions log structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique prediction ID |
| customer_id | INT | FOREIGN KEY → customers.customer_id | Customer being predicted |
| user_id | INT | FOREIGN KEY → user.id | User who made prediction |
| model_version | VARCHAR(50) | NOT NULL | Model name/version used |
| prediction | INT | NOT NULL | Predicted class (0 or 1) |
| confidence_score | FLOAT | NULL | Prediction probability |
| cluster_id | INT | NULL | Customer cluster assignment |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Prediction timestamp |

### 3.1.4. Model Registry Table

**Purpose:** Central registry for all ML models with performance metrics and metadata.

**Table 3.4: Model registry structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Model record ID |
| model_name | VARCHAR(100) | UNIQUE, NOT NULL | Unique model name |
| model_type | ENUM('Single','Ensemble') | NOT NULL | Model category |
| algorithm | VARCHAR(50) | NOT NULL | Algorithm name |
| version | VARCHAR(20) | NOT NULL | Model version |
| auc_score | FLOAT | NULL | AUC-ROC score |
| accuracy | FLOAT | NULL | Accuracy score |
| precision_score | FLOAT | NULL | Precision score |
| recall_score | FLOAT | NULL | Recall score |
| f1_score | FLOAT | NULL | F1 score |
| is_active | BOOLEAN | DEFAULT FALSE | Active model flag |
| training_time | INT | NULL | Training duration (seconds) |
| trained_at | TIMESTAMP | NULL | Training timestamp |
| trained_by | VARCHAR(50) | NULL | Username who trained |
| model_path | VARCHAR(255) | NULL | File path to .pkl file |
| model_size_mb | FLOAT | NULL | Model file size |

**Current Model Registry:**

| Model Name | Algorithm | AUC | Accuracy | F1 | Status | Path |
|------------|-----------|-----|----------|-----|--------|------|
| XGBoost | XGBClassifier | 0.7604 | 0.812 | 0.745 | ✅ Active | outputs/models/xgb_model.pkl |
| LightGBM | LGBMClassifier | 0.7811 | 0.823 | 0.761 | Inactive | outputs/models/lgb_model.pkl |
| Logistic | LogisticRegression | 0.7099 | 0.775 | 0.698 | Inactive | outputs/models/lr_model.pkl |
| CatBoost | CatBoostClassifier | - | - | - | Untrained | - |
| RandomForest | RandomForestClassifier | - | - | - | Untrained | - |
| NeuralNet | TensorFlow/Keras | - | - | - | Untrained | - |
| Voting | VotingClassifier | - | - | - | Untrained | - |
| Stacking | StackingClassifier | - | - | - | Untrained | - |

### 3.1.5. Customer Clusters Table

**Purpose:** Store customer segmentation results from K-Means/DBSCAN clustering.

**Table 3.5: Customer clusters structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Cluster record ID |
| customer_id | INT | FOREIGN KEY → customers.customer_id | Customer ID |
| cluster_id | INT | NOT NULL | Cluster number (0-N) |
| risk_level | ENUM('Low','Medium','High','Critical') | NOT NULL | Risk category |
| algorithm | VARCHAR(20) | NOT NULL | Clustering algorithm |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Clustering timestamp |

### 3.1.6. Data Quality Log Table

**Purpose:** Log data quality issues detected by outlier detection algorithms.

**Table 3.6: Data quality log structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Log entry ID |
| customer_id | INT | FOREIGN KEY → customers.customer_id | Customer with issue |
| issue_type | VARCHAR(50) | NOT NULL | Type of quality issue |
| severity | ENUM('Low','Medium','High') | NOT NULL | Issue severity |
| description | TEXT | NULL | Detailed description |
| detected_by | VARCHAR(50) | NULL | Detection method |
| detected_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Detection timestamp |

### 3.1.7. AI Chat History Table

**Purpose:** Store conversation history with Gemini AI assistant.

**Table 3.7: AI chat history structure**

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Chat message ID |
| user_id | INT | FOREIGN KEY → user.id | User who sent message |
| message | TEXT | NOT NULL | User message/question |
| response | TEXT | NOT NULL | AI response |
| context_type | ENUM('General','Prediction','Model','Report') | NOT NULL | Conversation context |
| context_data | JSON | NULL | Additional context |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Message timestamp |

### 3.1.8. Database Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────────┐
│    user     │         │   customers     │
├─────────────┤         ├─────────────────┤
│ id (PK)     │         │ customer_id(PK) │
│ username    │         │ LIMIT_BAL       │
│ role        │         │ SEX, EDUCATION  │
└──────┬──────┘         │ MARRIAGE, AGE   │
       │                │ PAY_1..PAY_12   │
       │                │ BILL_AMT1..12   │
       │                │ PAY_AMT1..12    │
       │                └────────┬────────┘
       │                         │
       │                         │
       ├─────────────┬───────────┼────────────┬─────────────┐
       │             │           │            │             │
       ▼             ▼           ▼            ▼             ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐
│predictions   │ │ai_chat      │ │customer      │ │data_quality    │
│   _log       │ │  _history   │ │ _clusters    │ │    _log        │
├──────────────┤ ├─────────────┤ ├──────────────┤ ├────────────────┤
│ id (PK)      │ │ id (PK)     │ │ id (PK)      │ │ id (PK)        │
│ customer_id  │ │ user_id(FK) │ │ customer_id  │ │ customer_id(FK)│
│ user_id (FK) │ │ message     │ │ cluster_id   │ │ issue_type     │
│ model_version│ │ response    │ │ risk_level   │ │ severity       │
│ prediction   │ │ context     │ │ algorithm    │ │ description    │
│ confidence   │ └─────────────┘ └──────────────┘ └────────────────┘
│ cluster_id   │
└──────────────┘

       ┌──────────────────┐
       │ model_registry   │
       ├──────────────────┤
       │ id (PK)          │
       │ model_name       │
       │ algorithm        │
       │ auc_score        │
       │ accuracy         │
       │ is_active        │
       │ trained_by       │
       │ model_path       │
       └──────────────────┘
```

## 3.2. Backend Services

The application follows a service-oriented architecture with clear separation of concerns.

### 3.2.1. Database Connector (`database/connector.py`)

**Responsibilities:**
- Manage MySQL connections with connection pooling
- Execute parameterized queries to prevent SQL injection
- Auto-create database if not exists (errno 1049 handling)
- Provide context manager interface for resource cleanup

**Key Methods:**
```python
class DatabaseConnector:
    def connect() -> bool
    def execute_query(query: str, params: Tuple) -> bool
    def fetch_all(query: str, params: Tuple) -> List[Tuple]
    def fetch_one(query: str, params: Tuple) -> Tuple
    def close() -> None
```

### 3.2.2. Authentication Service (`services/auth_service.py`)

**Responsibilities:**
- User login with bcrypt password verification
- Session management
- Update last_login timestamp

**Key Methods:**
```python
class AuthService:
    def login(username: str, password: str) -> Optional[User]
    def logout(user: User) -> None
```

### 3.2.3. ML Service (`services/ml_service.py`)

**Responsibilities:**
- Load active model from disk
- Make predictions on customer data
- Return prediction with confidence score

**Key Methods:**
```python
class MLService:
    def __init__(model_name: str)
    def predict(customer_data: dict) -> dict
    def predict_proba(customer_data: dict) -> np.ndarray
```

### 3.2.4. Model Management Service (`services/model_management_service.py`)

**Responsibilities:**
- Manage model lifecycle (train, save, load, delete)
- Switch active model
- Compare model performance
- Update model registry

**Key Methods:**
```python
class ModelManagementService:
    def get_all_models() -> List[dict]
    def get_active_model() -> dict
    def set_active_model(model_name: str, username: str) -> bool
    def train_model(model_name, X_train, y_train, X_test, y_test, 
                    username: str, progress_callback) -> dict
    def delete_model(model_name: str) -> bool
    def load_model(model_name: str) -> Any
    def compare_models(model_names: List, X_test, y_test) -> dict
```

**Training Flow:**
1. Create model instance via `_create_model()` factory
2. Fit model on training data
3. Evaluate on test data (AUC, accuracy, precision, recall, F1)
4. Serialize model to `outputs/models/*.pkl`
5. Insert/update model_registry record
6. Return metrics dictionary

### 3.2.5. Data Quality Service (`services/data_quality_service.py`)

**Responsibilities:**
- Detect outliers using IsolationForest, LOF, or Z-Score
- Cluster customers using K-Means or DBSCAN
- Analyze customer data quality issues
- Log findings to database

**Key Methods:**
```python
class DataQualityService:
    def detect_outliers(method: str, contamination: float) -> dict
    def cluster_customers(algorithm: str, n_clusters: int) -> dict
    def _analyze_customer_issues(customer_row) -> List[str]
    def log_outlier(customer_id: int, method: str, issues: List) -> None
    def delete_customer(customer_id: int) -> bool
```

**Outlier Detection Methods:**
- **IsolationForest**: Isolates anomalies using random partitioning
- **LocalOutlierFactor (LOF)**: Detects outliers based on local density
- **Z-Score**: Statistical method based on standard deviations

**Clustering Algorithms:**
- **K-Means**: Partitions customers into K clusters based on feature similarity
- **DBSCAN**: Density-based clustering, can identify noise points

### 3.2.6. Gemini Service (`services/gemini_service.py`)

**Responsibilities:**
- Initialize Gemini AI model with configuration
- Handle chat conversations with context
- Generate prediction explanations
- Compare model predictions
- Generate reports

**Key Methods:**
```python
class GeminiService:
    def __init__(db_connector: DatabaseConnector, user_id: int)
    def is_available() -> bool
    def send_message(message: str, context: dict, 
                     context_type: str) -> str
    def explain_prediction(customer_data: dict, 
                          prediction_result: dict) -> str
    def compare_models(customer_data: dict, predictions: dict) -> str
    def generate_report(stats: dict, report_type: str) -> str
    def get_chat_history(limit: int) -> List[dict]
    def clear_chat_history() -> None
```

**Configuration (`config/gemini_config.py`):**
```python
class GeminiConfig:
    API_KEY = "<your-api-key>"
    MODEL_NAME = "gemini-2.5-flash"
    TEMPERATURE = 0.7
    TOP_P = 0.95
    TOP_K = 40
    MAX_OUTPUT_TOKENS = 2048
    SYSTEM_INSTRUCTION = """Expert credit risk analyst..."""
```

### 3.2.7. Query Service (`services/query_service.py`)

**Responsibilities:**
- Read-only database queries for UI
- Format query results for display
- Aggregate statistics

**Key Methods:**
```python
class QueryService:
    def get_customer_by_id(customer_id: int) -> dict
    def get_recent_predictions(limit: int) -> List[dict]
    def get_prediction_statistics() -> dict
```

## 3.3. User Interface Components

The application uses PyQt6 for desktop GUI with a modern, role-based tab interface.

### 3.3.1. Main Window (`ui/MainWindowEx.py`)

**Responsibilities:**
- Initialize application window
- Setup role-based tabs
- Handle logout
- Manage database connection lifecycle

**Tab Structure:**
```
User Role:
├── 📊 Dự Báo Rủi Ro (PredictionTabWidget)
├── 📈 Dashboard (DashboardTabWidget)
└── 🤖 AI Trợ Lý (AIAssistantWidget)

Admin Role:
├── 📊 Dự Báo Rủi Ro (PredictionTabWidget)
├── 📈 Dashboard (DashboardTabWidget)
├── 🤖 AI Trợ Lý (AIAssistantWidget)
├── 🎯 Quản Lý ML (ModelManagementWidget)
└── ⚙️ Hệ Thống (SystemManagementWidget)
```

**Code Structure:**
```python
class MainWindowEx(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, user: User):
        self.user = user
        self.setup_user_info()
        self.setup_tabs()
        self.setup_role_permissions()
        
    def setup_tabs(self):
        # Tab 1-3: All users
        self.prediction_widget = PredictionTabWidget(...)
        self.dashboard_widget = DashboardTabWidget(...)
        self.ai_assistant_widget = AIAssistantWidget(...)
        
        # Tab 4-5: Admin only
        if self.user.is_admin():
            self.model_management_widget = ModelManagementWidget(...)
            self.system_widget = SystemManagementWidget(...)
```

### 3.3.2. Prediction Tab Widget (`ui/PredictionTabWidget.py`)

**Features:**
- 41 input fields for customer features
- Prediction button with ML model invocation
- Result display (default/non-default, confidence, risk level)
- Model selector (Admin only)

**Layout:**
```
┌────────────────────────────────────┐
│  CREDIT RISK PREDICTION            │
├────────────────────────────────────┤
│  Demographic Info:                 │
│  ┌──────────────┐  ┌─────────────┐│
│  │ Credit Limit │  │ Age         ││
│  └──────────────┘  └─────────────┘│
│                                    │
│  Payment History (PAY_1 to PAY_12):│
│  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐ ...    │
│  │  ││  ││  ││  ││  ││  │         │
│  └──┘└──┘└──┘└──┘└──┘└──┘         │
│                                    │
│  [ Predict Risk ]                  │
│                                    │
│  Result:                           │
│  ┌────────────────────────────────┐│
│  │ ⚠️ HIGH RISK - Default Likely ││
│  │ Confidence: 78.5%              ││
│  │ Cluster: High Risk (Cluster 3)││
│  └────────────────────────────────┘│
└────────────────────────────────────┘
```

### 3.3.3. Dashboard Tab Widget (`ui/DashboardTabWidget.py`)

**Features:**
- Display evaluation charts (ROC curve, confusion matrix)
- Model performance comparison table
- Statistics summary

**Data Source:**
- Loads from `outputs/evaluation/evaluation_data.npz`
- Shows metrics for active model

### 3.3.4. AI Assistant Widget (`ui/AIAssistantWidget.py`)

**Features:**
- Chat interface with Gemini AI
- Context selector (General, Prediction, Model, Report)
- Quick action buttons ("Credit risk là gì?", "Top 3 yếu tố rủi ro", "Cách giảm rủi ro")
- Chat history (last 5 messages loaded on init)

**UI Components:**
```python
class AIAssistantWidget(QWidget):
    def __init__(self, user: User, db_connector: DatabaseConnector):
        self.gemini_service = GeminiService(db_connector, user.id)
        
        # Components
        self.chat_display = QTextEdit()  # Read-only HTML
        self.input_field = QLineEdit()
        self.context_selector = QComboBox()
        self.send_button = QPushButton("Gửi")
        
    def send_message(self):
        message = self.input_field.text()
        context_type = self.context_selector.currentText()
        response = self.gemini_service.send_message(message, None, context_type)
        self.append_message("User", message, "#3498db")
        self.append_message("AI", response, "#2ecc71")
```

### 3.3.5. Model Management Widget (`ui/ModelManagementWidget.py`)

**Admin-Only Features:**
- Table showing all 8 models with metrics
- Train button for each model
- Set Active button
- Delete button (for inactive models)
- Compare models button

**Table Columns:**
| Model | Algorithm | AUC | Accuracy | F1-Score | Trained | Status | Actions |
|-------|-----------|-----|----------|----------|---------|--------|---------|
| XGBoost | XGBClassifier | 0.7604 | 0.812 | 0.745 | 2024-11-15 | ✅ Active | [Delete] |
| LightGBM | LGBMClassifier | 0.7811 | 0.823 | 0.761 | 2024-11-14 | Inactive | [Set Active][Delete] |

**Training Flow:**
1. Admin selects model from dropdown
2. Clicks "Train Model"
3. Service loads data, trains, evaluates
4. Progress dialog shows training status
5. Model saved to disk and registry updated
6. Table refreshed with new metrics

### 3.3.6. System Management Widget (`ui/SystemManagementWidget.py`)

**Admin-Only Features:**
- Outlier detection panel
  - Method selector (IsolationForest, LOF, ZScore)
  - Contamination rate spinner (0.01-0.50)
  - Detect button
- Customer clustering panel
  - Algorithm selector (KMeans, DBSCAN)
  - Number of clusters spinner (2-10)
  - Cluster button
- Results table with customer IDs, risk levels, issues, actions

**Worker Threads:**
```python
class DataQualityWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def run(self):
        # Long-running outlier detection
        result = self.service.detect_outliers(...)
        self.finished.emit(result)
```

## 3.4. Role-Based Access Control

### 3.4.1. User Model (`models/user.py`)

**Attributes:**
```python
class User:
    id: int
    username: str
    password_hash: str
    role: str  # 'User' or 'Admin'
    full_name: str
    email: str
    created_at: datetime
    last_login: datetime
    is_active: bool
```

**Permission Methods:**
```python
def is_admin(self) -> bool:
    return self.role == 'Admin'

def is_user(self) -> bool:
    return self.role == 'User'

def has_access_to_prediction(self) -> bool:
    return True  # All users

def has_access_to_reports(self) -> bool:
    return True  # All users

def has_access_to_ai_assistant(self) -> bool:
    return True  # All users

def has_access_to_model_management(self) -> bool:
    return self.is_admin()

def has_access_to_system_management(self) -> bool:
    return self.is_admin()

def can_select_model(self) -> bool:
    return self.is_admin()

def can_train_model(self) -> bool:
    return self.is_admin()

def can_view_all_predictions(self) -> bool:
    return self.is_admin()
```

### 3.4.2. Permission Enforcement

**UI Level:**
```python
# MainWindowEx.setup_tabs()
if self.user.is_admin():
    # Show admin tabs
    self.ui.tabWidget.addTab(self.model_management_widget, "🎯 Quản Lý ML")
    self.ui.tabWidget.addTab(self.system_widget, "⚙️ Hệ Thống")
```

**Widget Level:**
```python
# ModelManagementWidget.__init__()
if not self.user.is_admin():
    warning = QLabel("⚠️ Bạn không có quyền truy cập tab này")
    layout.addWidget(warning)
    return
```

**Service Level:**
```python
# ModelManagementService.train_model()
if not user.can_train_model():
    raise PermissionError("User does not have permission to train models")
```

### 3.4.3. Access Control Matrix

| Feature | User | Admin |
|---------|------|-------|
| View Prediction Tab | ✅ | ✅ |
| Make Predictions | ✅ | ✅ |
| Select Model | ❌ | ✅ |
| View Dashboard | ✅ | ✅ |
| Use AI Assistant | ✅ | ✅ |
| View Chat History | Own Only | Own Only |
| View Model Management | ❌ | ✅ |
| Train Models | ❌ | ✅ |
| Set Active Model | ❌ | ✅ |
| Delete Models | ❌ | ✅ |
| View System Management | ❌ | ✅ |
| Detect Outliers | ❌ | ✅ |
| Cluster Customers | ❌ | ✅ |
| View All Predictions | ❌ | ✅ |

---

*Continue to Chapter 4...*
