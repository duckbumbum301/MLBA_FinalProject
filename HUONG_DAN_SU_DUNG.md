# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG

## 🚀 Chạy Ứng Dụng

**Cách duy nhất để chạy:**
```bash
py -3.12 main.py
```

hoặc

```bash
python main.py
```

## 👤 Đăng Nhập

Sau khi chạy sẽ hiển thị màn hình login. Sử dụng các tài khoản có sẵn:

**User thường:**
- Username: `momshark`
- Password: `momshark`

**Admin:**
- Username: `fathershark`
- Password: `fathershark`

## 📊 Tính Năng Chính

### Tab "Dự Báo"
1. **💱 Currency Selector**: Chọn VND hoặc NT$ (mặc định VND, tỷ giá 1:800)
2. **🔍 Tìm kiếm khách hàng**: Nhập CMND 12 số → Click "Tìm kiếm"
3. **💾 Lưu khách hàng**: Điền form → Click "Lưu Khách Hàng" (Create/Update)
4. **🗑️ Xóa khách hàng**: Nhập CMND → Click "Xóa Khách Hàng"
5. **🎲 Random**: Tạo dữ liệu ngẫu nhiên 6/12 tháng
6. **📈 Dự đoán**: Xem kết quả rủi ro vỡ nợ

### Dữ Liệu Test
- Có **201 khách hàng** trong database để test tìm kiếm
- CMND mẫu: `123456789012`, `234567890123`, etc.

## 🎯 Lưu Ý Quan Trọng

1. **Chỉ chạy từ `main.py`** - Không sử dụng file khác
2. **Model đã train với NT$** - UI tự động chuyển đổi VND↔NT$
3. **Không cần retrain** khi chuyển đổi tiền tệ
4. **Database**: MySQL (credit_risk_db) phải đang chạy

## 🛠️ Cấu Trúc Code

```
MLBA_FinalProject/
├── main.py                    # ⭐ ENTRY POINT DUY NHẤT
├── ui/
│   ├── LoginPage.py          # Màn hình login
│   ├── MainWindow.py         # Main window với tabs
│   └── PredictionTabWidget.py # Tab dự đoán (đầy đủ tính năng)
├── services/
│   └── query_service.py      # CRUD operations
└── ml/
    └── predictor.py          # ML models
```

## ❌ Các File Không Dùng

- ~~`ui/run_ui.py`~~ (đã xóa)
- ~~`ui/PredictionTab.py`~~ (đã xóa)
- ~~`ui/MainWindowEx.py`~~ (đã xóa)

Chỉ sử dụng **`main.py`** để chạy!
