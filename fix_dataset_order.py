"""
Fix dataset column order để match với FEATURE_NAMES
"""
import pandas as pd

# Đọc dataset
df = pd.read_csv('UCI_Credit_Card_12months.csv')

# Thứ tự ĐÚNG
correct_order = [
    'ID', 'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
    'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
    'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12',
    'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
    'BILL_AMT7', 'BILL_AMT8', 'BILL_AMT9', 'BILL_AMT10', 'BILL_AMT11', 'BILL_AMT12',
    'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
    'PAY_AMT7', 'PAY_AMT8', 'PAY_AMT9', 'PAY_AMT10', 'PAY_AMT11', 'PAY_AMT12',
    'default.payment.next.month'
]

# Sắp xếp lại columns
df_fixed = df[correct_order]

# Backup dataset cũ
df.to_csv('UCI_Credit_Card_12months_OLD.csv', index=False)
print("✓ Đã backup dataset cũ: UCI_Credit_Card_12months_OLD.csv")

# Lưu dataset mới
df_fixed.to_csv('UCI_Credit_Card_12months.csv', index=False)
print("✓ Đã fix dataset: UCI_Credit_Card_12months.csv")
print(f"Thứ tự columns: {df_fixed.columns.tolist()[:20]}")
