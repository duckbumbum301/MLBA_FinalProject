"""
Preprocess Module
Chuẩn hóa dữ liệu input trước khi đưa vào ML model - Mở rộng lên 41 features (12 tháng)
"""
import numpy as np
import pandas as pd
from typing import Dict, List


# Thứ tự chuẩn của 41 features (mở rộng từ UCI dataset lên 12 tháng)
FEATURE_NAMES = [
    'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
    'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
    'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
    'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
    'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12',
    'BILL_AMT7', 'BILL_AMT8', 'BILL_AMT9', 'BILL_AMT10', 'BILL_AMT11', 'BILL_AMT12',
    'PAY_AMT7', 'PAY_AMT8', 'PAY_AMT9', 'PAY_AMT10', 'PAY_AMT11', 'PAY_AMT12'
]


def validate_input(input_dict: Dict) -> bool:
    """
    Kiểm tra input có đầy đủ 41 trường không
    
    Args:
        input_dict: Dict chứa input features
    
    Returns:
        True nếu hợp lệ, False nếu thiếu trường
    """
    missing_fields = [f for f in FEATURE_NAMES if f not in input_dict]
    
    if missing_fields:
        print(f"✗ Thiếu các trường: {missing_fields}")
        return False
    
    return True


def clean_input(input_dict: Dict) -> Dict:
    """
    Làm sạch và chuẩn hóa dữ liệu input (áp dụng logic giống notebook)
    
    Args:
        input_dict: Dict chứa raw input
    
    Returns:
        Dict đã được clean
    """
    cleaned = input_dict.copy()
    
    # 1. Chuẩn hóa EDUCATION: {0,4,5,6} -> 4 (others)
    if cleaned['EDUCATION'] in [0, 4, 5, 6]:
        cleaned['EDUCATION'] = 4
    
    # 2. Chuẩn hóa MARRIAGE: {0} -> 3 (others)
    if cleaned['MARRIAGE'] == 0:
        cleaned['MARRIAGE'] = 3
    
    # 3. Clip PAY_* về dải [-2, 9] cho tất cả 12 tháng
    pay_fields = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
                  'PAY_7', 'PAY_8', 'PAY_9', 'PAY_10', 'PAY_11', 'PAY_12']
    for field in pay_fields:
        cleaned[field] = max(-2, min(9, cleaned[field]))
    
    return cleaned


def preprocess_input(input_dict: Dict) -> pd.DataFrame:
    """
    Chuẩn hóa input dictionary thành DataFrame 1 hàng để đưa vào model
    
    Args:
        input_dict: Dict chứa 41 trường features
    
    Returns:
        DataFrame với 1 hàng, 41 cột theo đúng thứ tự
    
    Raises:
        ValueError: Nếu input không hợp lệ
    """
    # Validate
    if not validate_input(input_dict):
        raise ValueError("Input không hợp lệ - thiếu trường bắt buộc")
    
    # Clean
    cleaned = clean_input(input_dict)
    
    # Tạo DataFrame với đúng thứ tự cột - CÁCH ĐÚNG: dùng list của list
    # Đảm bảo 100% đúng thứ tự FEATURE_NAMES
    row_data = [[cleaned[field] for field in FEATURE_NAMES]]
    df = pd.DataFrame(row_data, columns=FEATURE_NAMES)
    
    return df


def batch_preprocess_inputs(input_list: List[Dict]) -> pd.DataFrame:
    """
    Chuẩn hóa nhiều input cùng lúc
    
    Args:
        input_list: List các dict input
    
    Returns:
        DataFrame với nhiều hàng
    """
    dfs = []
    for input_dict in input_list:
        df = preprocess_input(input_dict)
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)


def get_feature_names() -> List[str]:
    """
    Lấy danh sách tên 41 features theo thứ tự chuẩn
    
    Returns:
        List tên features
    """
    return FEATURE_NAMES.copy()
