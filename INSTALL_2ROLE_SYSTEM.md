# ========================================
# HƯỚNG DẪN CÀI ĐẶT HỆ THỐNG 2-ROLE + AI
# ========================================

## BƯỚC 1: Cài đặt Python packages mới

Chạy lệnh sau để cài đặt các packages bổ sung:

```powershell
pip install tensorflow google-generativeai
```

Hoặc cài từ requirements.txt:

```powershell
pip install -r requirements.txt
```

## BƯỚC 2: Cập nhật Database Schema

Chạy script update database:

```powershell
python update_database_schema.py
```

Script này sẽ:
- ✅ Update bảng `user` từ 3 roles → 2 roles (User/Admin)
- ✅ Tạo bảng `model_registry` - quản lý 8 models
- ✅ Tạo bảng `customer_clusters` - phân cụm khách hàng
- ✅ Tạo bảng `data_quality_log` - theo dõi data quality
- ✅ Tạo bảng `ai_chat_history` - lịch sử chat Gemini
- ✅ Update bảng `predictions_log` - thêm user_id, model_version, confidence_score

## BƯỚC 3: Cấu hình Gemini AI

1. Lấy API key miễn phí tại: https://makersuite.google.com/app/apikey

2. Mở file `config/gemini_config.py`

3. Thay đổi dòng:
   ```python
   API_KEY = "YOUR_API_KEY_HERE"
   ```
   
   Thành:
   ```python
   API_KEY = "AIzaSy..."  # API key của bạn
   ```

**LƯU Ý:** Nếu không có API key, tính năng AI Assistant sẽ hiện thông báo "Chưa cấu hình" nhưng hệ thống vẫn hoạt động bình thường.

## BƯỚC 4: Train thêm models mới (Tùy chọn)

Hiện tại hệ thống đã có 3 models:
- ✅ XGBoost (AUC 0.76)
- ✅ LightGBM (AUC 0.78)  
- ✅ LogisticRegression (AUC 0.71)

Để train thêm models khác, sau khi login với Admin account, vào:
**Tab "Quản Lý ML" → Click "Train New Model"**

Có thể train:
- CatBoost
- Random Forest
- Neural Network
- Voting Ensemble
- Stacking Ensemble

## BƯỚC 5: Khởi động ứng dụng

```powershell
python -m tests.test_app
```

## BƯỚC 6: Đăng nhập và test

**User account:**
- Username: `babyshark`
- Password: `123`
- Role: User
- Thấy: 3 tabs (Dự Báo, Báo Cáo, AI Trợ Lý)

**Admin account:**
- Username: `fathershark`
- Password: `123`
- Role: Admin
- Thấy: 5 tabs (Dự Báo, Báo Cáo, AI Trợ Lý, Quản Lý ML, Hệ Thống)

## CẤU TRÚC MỚI

```
MLBA_FinalProject/
├── config/
│   ├── database_config.py
│   └── gemini_config.py          ⭐ NEW
├── database/
│   └── credit_scoring/
│       ├── user.sql               ✏️ UPDATED (2 roles)
│       ├── predictions_log.sql    ✏️ UPDATED
│       ├── model_registry.sql     ⭐ NEW
│       ├── customer_clusters.sql  ⭐ NEW
│       ├── data_quality_log.sql   ⭐ NEW
│       └── ai_chat_history.sql    ⭐ NEW
├── services/
│   ├── auth_service.py            ✏️ UPDATED
│   ├── model_management_service.py ⭐ NEW
│   ├── gemini_service.py          ⭐ NEW
│   └── ... (existing services)
├── models/
│   └── user.py                    ✏️ UPDATED (2 roles)
├── requirements.txt               ✏️ UPDATED
└── update_database_schema.py      ⭐ NEW
```

## TÍNH NĂNG MỚI

### 🎯 User (Nhân viên văn phòng)
- ✅ Tab 1: Dự Báo - Nhập data, dự báo với active model
- ✅ Tab 2: Báo Cáo - Xem lịch sử của mình, export Excel/PDF
- ✅ Tab 3: AI Trợ Lý - Chat giải thích kết quả

### 🔐 Admin (Quản trị viên)
- ✅ Tab 1-3: Tất cả quyền của User + thêm:
  - Chọn model bất kỳ để test
  - So sánh 8 models cùng lúc
  - Xem predictions của tất cả users
- ✅ Tab 4: Quản Lý ML
  - Train/retrain models
  - Switch active model
  - Compare model performance
  - View ROC curves, metrics
- ✅ Tab 5: Hệ Thống
  - Detect outliers (Isolation Forest, LOF)
  - Customer clustering (K-Means)
  - View system stats
  - Manage users

## TROUBLESHOOTING

### Lỗi: "No module named 'google.generativeai'"
```powershell
pip install google-generativeai
```

### Lỗi: "No module named 'tensorflow'"
```powershell
pip install tensorflow
```

### Lỗi database connection
- Kiểm tra MySQL đang chạy
- Kiểm tra `config/database_config.py`
- Chạy lại `update_database_schema.py`

### AI Assistant không hoạt động
- Kiểm tra API key trong `config/gemini_config.py`
- Kiểm tra internet connection
- API key có thể cần thời gian kích hoạt (5-10 phút sau khi tạo)

## HỖ TRỢ

Nếu gặp lỗi, check:
1. Terminal output khi chạy `update_database_schema.py`
2. MySQL có tables mới chưa: `SHOW TABLES;`
3. User roles đã update chưa: `SELECT username, role FROM user;`

---

**Chúc bạn triển khai thành công! 🚀**
