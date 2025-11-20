"""
Script tạo test prediction với user_id=1
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
import json

config = DatabaseConfig()
db = DatabaseConnector(config)
db.connect()

print("\n" + "="*60)
print("TẠO TEST PREDICTION VỚI USER_ID=1")
print("="*60)

# Tạo test data
test_input = {
    'LIMIT_BAL': 100000,
    'SEX': 1,
    'EDUCATION': 2,
    'MARRIAGE': 1,
    'AGE': 30,
    'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0, 'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
    'PAY_7': 0, 'PAY_8': 0, 'PAY_9': 0, 'PAY_10': 0, 'PAY_11': 0, 'PAY_12': 0,
    'BILL_AMT1': 50000, 'BILL_AMT2': 50000, 'BILL_AMT3': 50000, 'BILL_AMT4': 50000,
    'BILL_AMT5': 50000, 'BILL_AMT6': 50000, 'BILL_AMT7': 50000, 'BILL_AMT8': 50000,
    'BILL_AMT9': 50000, 'BILL_AMT10': 50000, 'BILL_AMT11': 50000, 'BILL_AMT12': 50000,
    'PAY_AMT1': 50000, 'PAY_AMT2': 50000, 'PAY_AMT3': 50000, 'PAY_AMT4': 50000,
    'PAY_AMT5': 50000, 'PAY_AMT6': 50000, 'PAY_AMT7': 50000, 'PAY_AMT8': 50000,
    'PAY_AMT9': 50000, 'PAY_AMT10': 50000, 'PAY_AMT11': 50000, 'PAY_AMT12': 50000
}

# Tạo 5 test predictions
for i in range(5):
    raw_json = json.dumps(test_input)
    query = """
        INSERT INTO predictions_log 
        (customer_id, model_name, predicted_label, probability, raw_input_json, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (None, 'XGBoost', 0, 0.15 + (i * 0.05), raw_json, 1)  # user_id=1
    success = db.execute_query(query, params)
    if success:
        print(f"✓ Đã tạo test prediction #{i+1} với user_id=1")
    else:
        print(f"✗ Lỗi tạo prediction #{i+1}")

# Verify
print("\n📊 Kiểm tra predictions với user_id=1:")
rows = db.fetch_all("""
    SELECT id, customer_id, user_id, predicted_label, probability, created_at
    FROM predictions_log
    WHERE user_id = 1
    ORDER BY id DESC
    LIMIT 10
""")

if rows:
    print(f"✓ Tìm thấy {len(rows)} predictions với user_id=1:")
    for r in rows:
        print(f"  ID={r[0]}, customer={r[1]}, user_id={r[2]}, label={r[3]}, prob={r[4]:.4f}, date={r[5]}")
else:
    print("✗ KHÔNG tìm thấy predictions nào với user_id=1!")

db.close()
print("\n" + "="*60)
print("✓ HOÀN TẤT")
print("="*60)
