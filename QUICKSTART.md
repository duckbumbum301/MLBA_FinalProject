# 🚀 QUICKSTART GUIDE - Credit Risk Scoring System

## ⚡ Các Bước Nhanh Để Chạy Ứng Dụng

### 1️⃣ Setup Environment (5 phút)

```powershell
# Tạo và activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Cài dependencies
pip install -r requirements.txt
```

### 2️⃣ Setup MySQL Database (3 phút)

```powershell
# Đăng nhập MySQL
mysql -u root -p

# Trong MySQL shell:
source database/credit_scoring/user.sql;
source database/credit_scoring/customers.sql;
source database/credit_scoring/predictions_log.sql;

# Kiểm tra
SELECT username, role FROM user;
# Phải thấy: babyshark, fathershark, momshark
```

**⚠️ LƯU Ý**: Password MySQL mặc định trong code là `@Obama123`. 
Nếu khác, sửa trong `config/database_config.py`.

### 3️⃣ Train ML Models (10-15 phút) ⚠️ BẮT BUỘC

```powershell
python ml/train_models.py
```

**Sẽ tạo**:
- `outputs/models/xgb_model.pkl`
- `outputs/models/lgbm_model.pkl`
- `outputs/models/lr_cal_model.pkl`
- `outputs/evaluation/evaluation_data.npz`

### 4️⃣ Chạy Ứng Dụng 🦈

```powershell
python -m tests.test_app
```

### 5️⃣ Đăng Nhập

Chọn 1 trong 3 users:

| Username | Password | Role | Quyền |
|----------|----------|------|-------|
| **babyshark** | 123 | Admin | ✅ Tất cả |
| **fathershark** | 123 | Technical | ✅ Prediction + Dashboard |
| **momshark** | 123 | Secretary | ✅ Chỉ Prediction |

---

## 🎯 Demo Nhanh - Dự Báo Rủi Ro

### Input Mẫu (Nguy cơ THẤP):

- **LIMIT_BAL**: 100,000 NT$
- **SEX**: 1 - Nam
- **EDUCATION**: 2 - Đại học
- **MARRIAGE**: 1 - Kết hôn
- **AGE**: 35

**Lịch sử thanh toán** (tất cả PAY_*): `0 - Trả đúng hạn`

**Chi tiết sao kê**:
- BILL_AMT1~6: 10000, 9000, 8000, 7000, 6000, 5000
- PAY_AMT1~6: 2000, 2000, 2000, 2000, 2000, 2000

**Kết quả**: 🟢 Nguy cơ thấp (~15%)

---

### Input Mẫu (Nguy cơ CAO):

- **LIMIT_BAL**: 50,000 NT$
- **AGE**: 25

**Lịch sử thanh toán**: 
- PAY_0: `3 - Trễ 3 tháng`
- PAY_2: `2 - Trễ 2 tháng`
- PAY_3~6: `1 - Trễ 1 tháng`

**Chi tiết sao kê**:
- BILL_AMT1~6: 45000, 44000, 43000, 42000, 41000, 40000
- PAY_AMT1~6: 1000, 1000, 1000, 1000, 1000, 1000

**Kết quả**: 🔴 Nguy cơ cao (~85%)

---

## 🐛 Troubleshooting Nhanh

### ❌ "Can't connect to MySQL"

```python
# Kiểm tra trong config/database_config.py
password='@Obama123'  # ← Sửa thành password MySQL của bạn
```

### ❌ "Model file not found"

```powershell
# Chạy training
python ml/train_models.py
```

### ❌ "UCI_Credit_Card.csv not found"

- Đặt file CSV ở thư mục gốc `d:\MLBA_FinalProject\`

### ❌ Import errors

```powershell
# Cài lại dependencies
pip install -r requirements.txt
```

---

## 📂 Files Quan Trọng

| File | Mô Tả |
|------|-------|
| `ml/train_models.py` | ⚠️ Chạy đầu tiên để train models |
| `tests/test_app.py` | ⚠️ Entry point - chạy ứng dụng |
| `config/database_config.py` | 🔧 Sửa password MySQL ở đây |
| `database/credit_scoring/user.sql` | 👥 Demo users (babyshark, etc.) |

---

## 🎨 Features Chính

### Tab "Dự Báo Rủi Ro"
- ✅ 41 trường input (12 tháng lịch sử - mở rộng từ UCI dataset)
- ✅ 3 nhóm rõ ràng: Cá nhân / Lịch sử thanh toán (12 tháng) / Chi tiết sao kê (12 tháng)
- ✅ Kết quả màu sắc: Xanh (thấp) / Đỏ (cao)
- ✅ Xác suất phần trăm
- ✅ Lưu vào database (optional)

### Tab "Dashboard" (Admin/Technical only)
- 📊 Feature Importance (PAY_0 thường top 1)
- 📊 Confusion Matrix
- 📊 ROC Curves (3 models)
- 📊 Risk Distribution

---

## 💡 Tips

1. **Phân quyền**: Login với `babyshark` (Admin) để xem tất cả
2. **Lịch sử thanh toán**: PAY_0 (tháng gần nhất) quan trọng nhất!
3. **Refresh Dashboard**: Click nút 🔄 để reload data
4. **Clear Form**: Nút "Xóa Form" để reset input

---

## 📝 Next Steps

Sau khi chạy thành công:

1. ✅ Test với các input khác nhau
2. ✅ Kiểm tra database (predictions_log table)
3. ✅ Xem dashboard với từng role
4. ✅ Test logout/login flow

---

**Chúc bạn thành công! 🦈💳**

Xem chi tiết hơn trong `README.md` và `docs/STRUCTURE.md`.
