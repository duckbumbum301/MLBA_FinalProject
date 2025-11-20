"""
Script update tất cả predictions cũ (user_id=NULL) thành user_id=1
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig

config = DatabaseConfig()
db = DatabaseConnector(config)
db.connect()

print("\n" + "="*60)
print("CẬP NHẬT PREDICTIONS CŨ")
print("="*60)

# Đếm predictions có user_id=NULL
count_result = db.fetch_one("SELECT COUNT(*) FROM predictions_log WHERE user_id IS NULL")
null_count = count_result[0] if count_result else 0
print(f"\n📊 Tìm thấy {null_count} predictions có user_id=NULL")

if null_count > 0:
    # Update tất cả predictions NULL thành user_id=1
    update_query = """
        UPDATE predictions_log 
        SET user_id = 1 
        WHERE user_id IS NULL
    """
    success = db.execute_query(update_query)
    
    if success:
        print(f"✓ Đã cập nhật {null_count} predictions thành user_id=1")
    else:
        print("✗ Lỗi khi update!")
else:
    print("✓ Không có predictions nào cần update")

# Verify
print("\n📊 Kiểm tra sau khi update:")
total = db.fetch_one("SELECT COUNT(*) FROM predictions_log")[0]
with_user = db.fetch_one("SELECT COUNT(*) FROM predictions_log WHERE user_id = 1")[0]
print(f"  Tổng predictions: {total}")
print(f"  Có user_id=1: {with_user}")
print(f"  Còn NULL: {total - with_user}")

# Show 10 predictions mới nhất
print("\n📋 10 predictions mới nhất:")
rows = db.fetch_all("""
    SELECT p.id, c.customer_name, p.user_id, p.predicted_label, p.probability, p.created_at
    FROM predictions_log p
    LEFT JOIN customers c ON p.customer_id = c.id
    ORDER BY p.id DESC
    LIMIT 10
""")

for r in rows:
    name = r[1] or '-'
    print(f"  ID={r[0]}, name={name:20s}, user_id={r[2]}, label={r[3]}, prob={r[4]:.4f}, date={r[5]}")

db.close()
print("\n" + "="*60)
print("✓ HOÀN TẤT")
print("="*60)
