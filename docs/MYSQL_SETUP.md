# 🗄️ MySQL Setup Guide - Windows

Hướng dẫn cài đặt và setup MySQL cho Credit Risk System trên Windows.

---

## Phương Án 1: MySQL Server (Recommended)

### Bước 1: Download MySQL

1. Truy cập: https://dev.mysql.com/downloads/installer/
2. Download **MySQL Installer for Windows** (file `.msi`)
3. Chọn phiên bản **mysql-installer-community**

### Bước 2: Cài Đặt MySQL

1. Chạy file installer
2. Chọn **Developer Default** hoặc **Custom**
3. **Components cần cài**:
   - MySQL Server 8.0 (hoặc 5.7+)
   - MySQL Workbench (optional - GUI tool)
   - MySQL Shell (optional)

4. **Configuration**:
   - Port: `3306` (default)
   - Root Password: Nhập password (ví dụ: `@Obama123`)
   - ✅ Nhớ password này!

5. Hoàn tất cài đặt

### Bước 3: Kiểm Tra MySQL Service

```powershell
# Kiểm tra service đang chạy
Get-Service MySQL*

# Nếu chưa chạy, start service
Start-Service MySQL80  # Tên có thể khác (MySQL57, MySQL, etc.)
```

### Bước 4: Test Kết Nối

```powershell
# Đăng nhập MySQL command line
mysql -u root -p
# Nhập password đã đặt

# Trong MySQL shell:
mysql> SELECT VERSION();
mysql> EXIT;
```

---

## Phương Án 2: XAMPP (Easier for Beginners)

### Bước 1: Download XAMPP

1. Truy cập: https://www.apachefriends.org/download.html
2. Download XAMPP for Windows
3. Chạy installer

### Bước 2: Start MySQL

1. Mở **XAMPP Control Panel**
2. Click **Start** bên cạnh **MySQL**
3. Port mặc định: `3306`

### Bước 3: Set Root Password (Optional but Recommended)

```powershell
# Vào phpMyAdmin: http://localhost/phpmyadmin
# Hoặc dùng command line:

cd C:\xampp\mysql\bin
.\mysql.exe -u root

# Trong MySQL:
ALTER USER 'root'@'localhost' IDENTIFIED BY '@Obama123';
FLUSH PRIVILEGES;
EXIT;
```

---

## Setup Database cho Credit Risk System

### Option A: Sử dụng MySQL Command Line

```powershell
# 1. Đăng nhập MySQL
mysql -u root -p
# Nhập password

# 2. Tạo database
CREATE DATABASE IF NOT EXISTS credit_risk_db 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

# 3. Sử dụng database
USE credit_risk_db;

# 4. Chạy các SQL files
source D:/MLBA_FinalProject/database/credit_scoring/user.sql;
source D:/MLBA_FinalProject/database/credit_scoring/customers.sql;
source D:/MLBA_FinalProject/database/credit_scoring/predictions_log.sql;

# 5. Kiểm tra tables
SHOW TABLES;

# 6. Kiểm tra demo users
SELECT username, role FROM user;
```

### Option B: Sử dụng MySQL Workbench (GUI)

1. Mở **MySQL Workbench**
2. Connect tới localhost (root)
3. Chọn **File > Open SQL Script**
4. Chạy từng file:
   - `database/credit_scoring/user.sql`
   - `database/credit_scoring/customers.sql`
   - `database/credit_scoring/predictions_log.sql`
5. Execute mỗi script

---

## Update Password trong Project

Nếu password MySQL của bạn **KHÔNG PHẢI** `@Obama123`:

**Sửa file**: `config/database_config.py`

```python
class DatabaseConfig:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 3306,
        user: str = 'root',
        password: str = '@Obama123',  # ← THAY ĐỔI Ở ĐÂY
        database: str = 'credit_risk_db'
    ):
```

Thay `@Obama123` thành password thực tế của bạn.

---

## Troubleshooting

### ❌ "Can't connect to MySQL server on localhost"

**Giải pháp**:

1. Kiểm tra MySQL service đang chạy:
   ```powershell
   Get-Service MySQL*
   ```

2. Start service nếu stopped:
   ```powershell
   Start-Service MySQL80
   ```

3. Kiểm tra port 3306:
   ```powershell
   netstat -an | findstr 3306
   ```

### ❌ "Access denied for user 'root'@'localhost'"

**Giải pháp**:

- Sai password → Nhập đúng password đã đặt khi cài MySQL
- Update password trong `config/database_config.py`

### ❌ "Unknown database 'credit_risk_db'"

**Giải pháp**:

```sql
CREATE DATABASE credit_risk_db;
USE credit_risk_db;
source user.sql;
source customers.sql;
source predictions_log.sql;
```

### ❌ Port 3306 already in use

**Giải pháp**:

1. Stop process đang dùng port 3306
2. Hoặc đổi port MySQL (thay trong `database_config.py`)

---

## Test Connection bằng Python

Tạo file `test_db.py`:

```python
from config.database_config import DatabaseConfig
from database.connector import DatabaseConnector

config = DatabaseConfig.default()
db = DatabaseConnector(config)

if db.connect():
    print("✅ Connection successful!")
    
    # Test query
    result = db.fetch_one("SELECT VERSION()")
    print(f"MySQL version: {result[0]}")
    
    # Check tables
    tables = db.fetch_all("SHOW TABLES")
    print(f"Tables: {[t[0] for t in tables]}")
    
    db.close()
else:
    print("❌ Connection failed!")
```

Chạy:
```powershell
python test_db.py
```

---

## Demo Users

Sau khi chạy `user.sql`, sẽ có 3 users:

| Username | Password | Role | Hash (bcrypt) |
|----------|----------|------|---------------|
| babyshark | 123 | Admin | $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.4HYoVYYlDqBu |
| fathershark | 123 | Technical | (same hash) |
| momshark | 123 | Secretary | (same hash) |

**Test login**:
```sql
SELECT * FROM user WHERE username = 'babyshark';
```

---

## Next Steps

Sau khi MySQL ready:

1. ✅ Run: `python check_setup.py` để kiểm tra
2. ✅ Train models: `python ml/train_models.py`
3. ✅ Run app: `python -m tests.test_app`

---

**Chúc bạn setup thành công! 🗄️**
