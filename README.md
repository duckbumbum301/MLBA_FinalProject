# 🦈 Credit Risk Scoring System - PyQt6

## 📋 Giới Thiệu

Hệ thống **Credit Risk Scoring** là ứng dụng desktop PyQt6 dùng để dự báo rủi ro vỡ nợ của khách hàng ngân hàng. Ứng dụng tích hợp:

- ✅ **Machine Learning Models**: XGBoost, LightGBM, Logistic Regression
- ✅ **Giao diện PyQt6** thân thiện, dễ sử dụng
- ✅ **Hệ thống phân quyền** (Admin, Technical, Secretary)
- ✅ **Database MySQL** lưu trữ khách hàng và lịch sử dự báo
- ✅ **Dashboard trực quan** với 4 biểu đồ đánh giá mô hình

Dataset sử dụng: **UCI Credit Card Default** (mở rộng lên 41 features - 12 tháng lịch sử)

---

## 🚀 Cài Đặt & Chạy Ứng Dụng

### Bước 1: Clone Repository

```bash
git clone <repository_url>
cd MLBA_FinalProject
```

### Bước 2: Tạo Virtual Environment

```powershell
# Tạo venv
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Nếu gặp lỗi ExecutionPolicy, chạy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Bước 3: Cài Đặt Dependencies

```powershell
pip install -r requirements.txt
```

### Bước 4: Setup MySQL Database

1. **Khởi động MySQL Server** (port mặc định 3306)

2. **Tạo Database và Tables**:

```powershell
# Đăng nhập MySQL
mysql -u root -p

# Chạy setup script
source database/credit_scoring/setup.sql
```

Hoặc chạy từng file SQL:

```sql
CREATE DATABASE IF NOT EXISTS credit_risk_db;
USE credit_risk_db;

source database/credit_scoring/user.sql;
source database/credit_scoring/customers.sql;
source database/credit_scoring/predictions_log.sql;
```

3. **Kiểm tra users demo**:

```sql
USE credit_risk_db;
SELECT username, role FROM user;
```

Sẽ thấy 3 users:
- `babyshark` (Admin) - password: `123`
- `fathershark` (Technical) - password: `123`
- `momshark` (Secretary) - password: `123`

### Bước 5: Train ML Models

⚠️ **BẮT BUỘC**: Train models trước khi chạy ứng dụng!

```powershell
python ml/train_models.py
```

Script sẽ:
- Load và preprocess data từ `UCI_Credit_Card.csv`
- Train 3 models: XGBoost, LightGBM, Logistic Regression
- Lưu models vào `outputs/models/`
- Lưu evaluation data vào `outputs/evaluation/`

**Lưu ý**: Đảm bảo file `UCI_Credit_Card.csv` ở thư mục gốc project.

### Bước 6: Chạy Ứng Dụng

```powershell
python -m tests.test_app
```

---

## 🖥️ Sử Dụng Ứng Dụng

### 1. Đăng Nhập

- Username: `babyshark` / `fathershark` / `momshark`
- Password: `123`

### 2. Tab "Dự Báo Rủi Ro"

Nhập đầy đủ **41 trường** thông tin khách hàng:

**Nhóm 1: Thông tin cá nhân**
- Hạn mức thẻ (LIMIT_BAL)
- Giới tính (SEX): 1=Nam, 2=Nữ
- Trình độ học vấn (EDUCATION)
- Tình trạng hôn nhân (MARRIAGE)
- Tuổi (AGE)

**Nhóm 2: Lịch sử thanh toán** (12 tháng)
- PAY_0 ~ PAY_6: Trạng thái thanh toán
  - `-2`: Không sử dụng
  - `-1`, `0`: Trả đúng hạn
  - `1~9`: Trễ 1~9+ tháng

**Nhóm 3: Chi tiết sao kê** (12 tháng)
- BILL_AMT1 ~ BILL_AMT6: Số dư sao kê
- PAY_AMT1 ~ PAY_AMT6: Số tiền đã thanh toán

**Kết quả hiển thị**:
- ✅ **Nguy cơ cao** (màu đỏ) hoặc **Nguy cơ thấp** (màu xanh)
- ✅ **Xác suất vỡ nợ** (%)

**Tùy chọn**:
- ☑ Lưu vào lịch sử dự báo (database)

### 3. Tab "Dashboard"

Hiển thị 4 biểu đồ đánh giá mô hình:

1. **Feature Importance**: Top 10 features quan trọng nhất
   - PAY_0 (lịch sử thanh toán gần nhất) thường quan trọng nhất

2. **Confusion Matrix**: Ma trận nhầm lẫn của XGBoost
   - TP, TN, FP, FN

3. **ROC Curves**: So sánh 3 models
   - XGBoost, LightGBM, Logistic Regression
   - Hiển thị AUC score

4. **Risk Distribution**: Phân phối rủi ro theo bins xác suất

**Phân quyền Dashboard**:
- ✅ Admin: Xem được
- ✅ Technical: Xem được
- ❌ Secretary: Không xem được

---

## 📁 Cấu Trúc Dự Án

```
MLBA_FinalProject/
│
├── config/                      # Cấu hình database
│   ├── __init__.py
│   └── database_config.py
│
├── database/                    # Database connector & SQL
│   ├── __init__.py
│   ├── connector.py
│   └── credit_scoring/
│       ├── user.sql
│       ├── customers.sql
│       ├── predictions_log.sql
│       └── setup.sql
│
├── models/                      # Data models (Python classes)
│   ├── __init__.py
│   ├── user.py
│   ├── customer.py
│   └── prediction_result.py
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py          # Authentication & password hashing
│   ├── query_service.py         # Database queries
│   └── ml_service.py            # ML model interface
│
├── ml/                          # Machine Learning utilities
│   ├── __init__.py
│   ├── preprocess.py            # Data preprocessing
│   ├── predictor.py             # Model loading & prediction
│   ├── evaluation.py            # Evaluation & plotting
│   └── train_models.py          # Training script ⚠️
│
├── ui/                          # PyQt6 UI
│   ├── __init__.py
│   ├── LoginWindow.ui           # Qt Designer file
│   ├── LoginWindow.py           # Generated Python
│   ├── LoginWindowEx.py         # Logic implementation
│   ├── MainWindow.ui
│   ├── MainWindow.py
│   ├── MainWindowEx.py          # Main window logic
│   ├── PredictionTabWidget.py   # Prediction tab
│   └── DashboardTabWidget.py    # Dashboard tab
│
├── tests/
│   ├── __init__.py
│   └── test_app.py              # Entry point ⚠️
│
├── outputs/
│   ├── models/                  # Trained models (.pkl)
│   ├── charts/                  # Saved charts
│   └── evaluation/              # Evaluation data (.npz)
│
├── docs/                        # Documentation
│
├── UCI_Credit_Card.csv          # Dataset ⚠️
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔑 Phân Quyền Người Dùng

| Role | Username | Password | Quyền Truy Cập |
|------|----------|----------|----------------|
| **Admin** | babyshark | 123 | ✅ Tất cả tabs |
| **Technical** | fathershark | 123 | ✅ Dự báo + Dashboard |
| **Secretary** | momshark | 123 | ✅ Chỉ Dự báo |

---

## 🧪 Testing

### Test Database Connection

```python
from config.database_config import DatabaseConfig
from database.connector import DatabaseConnector

config = DatabaseConfig.default()
db = DatabaseConnector(config)
success = db.connect()
print("Connected!" if success else "Failed!")
db.close()
```

### Test ML Prediction

```python
from services.ml_service import MLService

ml_service = MLService(model_name='XGBoost')

input_data = {
    'LIMIT_BAL': 50000, 'SEX': 1, 'EDUCATION': 2,
    'MARRIAGE': 2, 'AGE': 30,
    'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0, 
    'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
    'BILL_AMT1': 10000, 'BILL_AMT2': 9000, 'BILL_AMT3': 8000,
    'BILL_AMT4': 7000, 'BILL_AMT5': 6000, 'BILL_AMT6': 5000,
    'PAY_AMT1': 2000, 'PAY_AMT2': 2000, 'PAY_AMT3': 2000,
    'PAY_AMT4': 2000, 'PAY_AMT5': 2000, 'PAY_AMT6': 2000
}

result = ml_service.predict_default_risk(input_data)
print(result)
```

---

## 🐛 Troubleshooting

### Lỗi: "Import mysql.connector could not be resolved"

```powershell
pip install mysql-connector-python
```

### Lỗi: "Can't connect to MySQL server"

- Kiểm tra MySQL đã chạy chưa
- Kiểm tra username/password trong `config/database_config.py`
- Kiểm tra port (mặc định 3306)

### Lỗi: "Model file not found"

- Chạy training script:
  ```powershell
  python ml/train_models.py
  ```

### Lỗi: "UCI_Credit_Card.csv not found"

- Đảm bảo file CSV ở thư mục gốc project
- Hoặc update đường dẫn trong `ml/train_models.py`

### Lỗi PyQt6 import

```powershell
pip install PyQt6
```

---

## 📊 Dataset Information

**UCI Credit Card Default Dataset**

- **Records**: 30,000 khách hàng
- **Features**: 41 trường (12 tháng lịch sử)
- **Target**: `default.payment.next.month` (1=vỡ nợ, 0=không vỡ nợ)
- **Imbalance**: ~22% positive class

**Key Features**:
- `PAY_0`: Trạng thái thanh toán tháng gần nhất (feature quan trọng nhất)
- `LIMIT_BAL`: Hạn mức thẻ
- `BILL_AMT1~12`: Số dư sao kê 12 tháng
- `PAY_AMT1~12`: Số tiền thanh toán 12 tháng

---

## 👨‍💻 Development

### Regenerate UI files từ .ui

Nếu chỉnh sửa `.ui` trong Qt Designer:

```powershell
pyuic6 ui/LoginWindow.ui -o ui/LoginWindow.py
pyuic6 ui/MainWindow.ui -o ui/MainWindow.py
```

### Add new user

```python
from services.auth_service import AuthService
from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig

config = DatabaseConfig.default()
db = DatabaseConnector(config)
db.connect()

auth = AuthService(db)
auth.create_user('newuser', 'password123', 'Technical')

db.close()
```

---

## 📝 License

This project is for educational purposes.

---

## 🦈 Credits

- **Developer**: BabyShark Team
- **Dataset**: UCI Machine Learning Repository
- **Framework**: PyQt6, scikit-learn, LightGBM, XGBoost

---

## 🎯 TODO / Future Improvements

- [ ] Add more models (CatBoost, Neural Networks)
- [ ] Implement model comparison tool
- [ ] Add export report to PDF
- [ ] Batch prediction from CSV file
- [ ] Real-time model monitoring
- [ ] User management UI (create/edit/delete users)

---

**Happy Credit Scoring! 🦈💳**
