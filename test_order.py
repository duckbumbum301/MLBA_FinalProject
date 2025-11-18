"""Test script để verify thứ tự features"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ml.preprocess import preprocess_input

# Test input
test_input = {
    'LIMIT_BAL': 50000, 'SEX': 1, 'EDUCATION': 2, 'MARRIAGE': 2, 'AGE': 30,
    'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0, 'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
    'PAY_7': 0, 'PAY_8': 0, 'PAY_9': 0, 'PAY_10': 0, 'PAY_11': 0, 'PAY_12': 0,
    'BILL_AMT1': 0, 'BILL_AMT2': 0, 'BILL_AMT3': 0, 'BILL_AMT4': 0, 'BILL_AMT5': 0, 'BILL_AMT6': 0,
    'BILL_AMT7': 0, 'BILL_AMT8': 0, 'BILL_AMT9': 0, 'BILL_AMT10': 0, 'BILL_AMT11': 0, 'BILL_AMT12': 0,
    'PAY_AMT1': 0, 'PAY_AMT2': 0, 'PAY_AMT3': 0, 'PAY_AMT4': 0, 'PAY_AMT5': 0, 'PAY_AMT6': 0,
    'PAY_AMT7': 0, 'PAY_AMT8': 0, 'PAY_AMT9': 0, 'PAY_AMT10': 0, 'PAY_AMT11': 0, 'PAY_AMT12': 0
}

df = preprocess_input(test_input)
print("✓ DataFrame columns:")
print(df.columns.tolist())
print("\n✓ Expected order: PAY_0-12, BILL_AMT1-12, PAY_AMT1-12")
print(f"\n✓ Match: {df.columns[5:17].tolist() == ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6', 'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12']}")
