"""
Expand Dataset from 6 to 12 months
Mở rộng UCI Credit Card dataset từ 6 tháng (PAY_0-6, BILL_AMT1-6, PAY_AMT1-6)
lên 12 tháng (thêm tháng 7-12) bằng cách sinh dữ liệu giả lập hợp lý
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
INPUT_FILE = ROOT / 'UCI_Credit_Card.csv'
OUTPUT_FILE = ROOT / 'UCI_Credit_Card_12months.csv'

def expand_to_12_months(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mở rộng dataset từ 6 tháng lên 12 tháng
    
    Chiến lược:
    - PAY_7-12: Giảm dần delay (giả sử xa hơn thì thanh toán tốt hơn)
    - BILL_AMT7-12: Giảm dần từ BILL_AMT6 (giả sử số dư giảm dần)
    - PAY_AMT7-12: Tương quan với BILL_AMT tương ứng
    """
    df_expanded = df.copy()
    
    # ========================================
    # 1. Expand PAY_7-12 (Payment Status)
    # ========================================
    # Giả lập: Các tháng càng xa thì payment status trung bình tốt hơn
    # PAY_7 base on PAY_6, PAY_8 base on PAY_7, ...
    
    for month in [7, 8, 9, 10, 11, 12]:
        prev_month = month - 1 if month > 7 else 6
        prev_col = f'PAY_{prev_month}'
        new_col = f'PAY_{month}'
        
        # Base on previous month with random noise
        # Giả lập: 70% giống tháng trước, 20% cải thiện (giảm 1), 10% xấu đi (tăng 1)
        df_expanded[new_col] = df_expanded[prev_col].copy()
        
        n = len(df_expanded)
        rand = np.random.rand(n)
        
        # 20% cases: improve (decrease by 1, but not below -2)
        improve_mask = rand < 0.20
        df_expanded.loc[improve_mask, new_col] = np.maximum(
            df_expanded.loc[improve_mask, new_col] - 1, -2
        )
        
        # 10% cases: worsen (increase by 1, but not above 9)
        worsen_mask = rand >= 0.90
        df_expanded.loc[worsen_mask, new_col] = np.minimum(
            df_expanded.loc[worsen_mask, new_col] + 1, 9
        )
    
    # ========================================
    # 2. Expand BILL_AMT7-12 (Bill Amount)
    # ========================================
    # Giả lập: Số dư giảm dần theo thời gian
    # BILL_AMT7 = BILL_AMT6 * random(0.85, 1.05)
    
    for month in [7, 8, 9, 10, 11, 12]:
        prev_month = month - 1 if month > 7 else 6
        prev_col = f'BILL_AMT{prev_month}'
        new_col = f'BILL_AMT{month}'
        
        # Random factor between 0.85-1.05
        factors = np.random.uniform(0.85, 1.05, size=len(df_expanded))
        df_expanded[new_col] = df_expanded[prev_col] * factors
        
        # Ensure non-negative
        df_expanded[new_col] = df_expanded[new_col].clip(lower=0)
    
    # ========================================
    # 3. Expand PAY_AMT7-12 (Payment Amount)
    # ========================================
    # Giả lập: Payment amount tương quan với bill amount
    # PAY_AMT = BILL_AMT * payment_ratio
    # payment_ratio depends on PAY status
    
    for month in [7, 8, 9, 10, 11, 12]:
        bill_col = f'BILL_AMT{month}'
        pay_status_col = f'PAY_{month}'
        new_col = f'PAY_AMT{month}'
        
        # Base ratio between 0-1
        payment_ratios = np.random.uniform(0.05, 0.95, size=len(df_expanded))
        
        # Adjust based on PAY status:
        # - If PAY <= 0 (paid on time): higher payment ratio
        # - If PAY > 0 (delayed): lower payment ratio
        pay_status = df_expanded[pay_status_col]
        
        # On-time payers (PAY <= 0): ratio between 0.6-1.0
        on_time_mask = pay_status <= 0
        payment_ratios[on_time_mask] = np.random.uniform(
            0.6, 1.0, size=on_time_mask.sum()
        )
        
        # Late payers (PAY > 0): ratio between 0.1-0.5
        late_mask = pay_status > 0
        payment_ratios[late_mask] = np.random.uniform(
            0.1, 0.5, size=late_mask.sum()
        )
        
        # Calculate PAY_AMT
        df_expanded[new_col] = df_expanded[bill_col] * payment_ratios
        
        # Ensure non-negative
        df_expanded[new_col] = df_expanded[new_col].clip(lower=0)
    
    return df_expanded


def main():
    """Main function"""
    print("=" * 70)
    print("EXPAND UCI CREDIT CARD DATASET: 6 MONTHS → 12 MONTHS")
    print("=" * 70)
    
    # Load original data
    print(f"\n1. Loading original data from: {INPUT_FILE}")
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"❌ File not found: {INPUT_FILE}")
    
    df = pd.read_csv(INPUT_FILE)
    print(f"   ✓ Original shape: {df.shape}")
    print(f"   ✓ Original columns: {df.shape[1]}")
    
    # Expand to 12 months
    print(f"\n2. Expanding to 12 months...")
    df_expanded = expand_to_12_months(df)
    print(f"   ✓ Expanded shape: {df_expanded.shape}")
    print(f"   ✓ Expanded columns: {df_expanded.shape[1]}")
    
    # Show new columns
    original_cols = set(df.columns)
    new_cols = set(df_expanded.columns) - original_cols
    print(f"\n3. New columns added ({len(new_cols)}):")
    for col in sorted(new_cols):
        print(f"   - {col}")
    
    # Save expanded data
    print(f"\n4. Saving expanded dataset to: {OUTPUT_FILE}")
    df_expanded.to_csv(OUTPUT_FILE, index=False)
    print(f"   ✓ Saved successfully!")
    
    # Statistics
    print(f"\n5. Dataset Statistics:")
    print(f"   - Records: {len(df_expanded):,}")
    print(f"   - Total features: {df_expanded.shape[1] - 2} (excluding ID and target)")
    print(f"   - Payment history: 12 months (PAY_0, PAY_2-12)")
    print(f"   - Bill amounts: 12 months (BILL_AMT1-12)")
    print(f"   - Payment amounts: 12 months (PAY_AMT1-12)")
    
    # Show sample
    print(f"\n6. Sample of new columns:")
    sample_cols = ['PAY_7', 'PAY_12', 'BILL_AMT7', 'BILL_AMT12', 'PAY_AMT7', 'PAY_AMT12']
    print(df_expanded[sample_cols].describe())
    
    print("\n" + "=" * 70)
    print("✅ EXPANSION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📁 Next steps:")
    print(f"   1. Use '{OUTPUT_FILE.name}' for training")
    print(f"   2. Update train_models.py to use this file")
    print(f"   3. Models will now support 41 features!")


if __name__ == '__main__':
    main()
