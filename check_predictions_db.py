"""
Script kiểm tra dữ liệu trong bảng predictions_log
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
print("KIỂM TRA DỮ LIỆU PREDICTIONS_LOG")
print("="*60)

# Check predictions_log - CHỈ LẤY MỚI NHẤT
rows = db.fetch_all("""
    SELECT p.id, p.customer_id, p.user_id, p.predicted_label, 
           p.probability, p.created_at, c.customer_name
    FROM predictions_log p
    LEFT JOIN customers c ON p.customer_id = c.id
    WHERE p.id >= 207
    ORDER BY p.id DESC 
    LIMIT 10
""")

if rows:
    print(f"\n✓ Tìm thấy {len(rows)} predictions:")
    for r in rows:
        print(f"  ID={r[0]}, customer_id={r[1]}, user_id={r[2]}, "
              f"label={r[3]}, prob={r[4]:.4f}, "
              f"date={r[5]}, name={r[6] or 'N/A'}")
else:
    print("\n✗ KHÔNG có dữ liệu trong predictions_log!")

# Check customers
customer_count = db.fetch_one("SELECT COUNT(*) FROM customers")[0]
print(f"\n📊 Tổng số customers: {customer_count}")

# Check by user_id
print("\n📊 Phân bổ theo user_id:")
user_stats = db.fetch_all("""
    SELECT user_id, COUNT(*) as count 
    FROM predictions_log 
    GROUP BY user_id
""")
for stat in user_stats:
    print(f"  User ID {stat[0]}: {stat[1]} predictions")

db.close()
print("\n" + "="*60)
