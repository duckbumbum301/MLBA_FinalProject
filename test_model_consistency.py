"""
Test script để verify model đang predict thực sự, không phải random
"""
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from services.ml_service import MLService

def test_prediction_consistency():
    """
    Test 1: Cùng input phải cho cùng output
    Nếu random thì mỗi lần predict sẽ khác nhau
    """
    print("\n" + "="*60)
    print("TEST 1: PREDICTION CONSISTENCY")
    print("="*60)
    
    # Input data giống như trong ảnh của bạn
    test_input = {
        'LIMIT_BAL': 500000000.00,
        'SEX': 1,
        'EDUCATION': 2,
        'MARRIAGE': 1,
        'AGE': 30,
        'PAY_0': 0,
        'PAY_2': 0,
        'PAY_3': 0,
        'PAY_4': 0,
        'PAY_5': 0,
        'PAY_6': 0,
        'PAY_7': 0,
        'PAY_8': 0,
        'PAY_9': 0,
        'PAY_10': 0,
        'PAY_11': 0,
        'PAY_12': 0,
        'BILL_AMT1': 20000.00,
        'BILL_AMT2': 40000000.00,
        'BILL_AMT3': 30000000.00,
        'BILL_AMT4': 15000000.00,
        'BILL_AMT5': 2000000.00,
        'BILL_AMT6': 500000.00,
        'BILL_AMT7': 30000000.00,
        'BILL_AMT8': 20000000.00,
        'BILL_AMT9': 15000000.00,
        'BILL_AMT10': 10000000.00,
        'BILL_AMT11': 8000000.00,
        'BILL_AMT12': 10000000.00,
        'PAY_AMT1': 16000000.00,
        'PAY_AMT2': 16000000.00,
        'PAY_AMT3': 16000000.00,
        'PAY_AMT4': 16000000.00,
        'PAY_AMT5': 16000000.00,
        'PAY_AMT6': 16000000.00,
        'PAY_AMT7': 16000000.00,
        'PAY_AMT8': 16000000.00,
        'PAY_AMT9': 16000000.00,
        'PAY_AMT10': 16000000.00,
        'PAY_AMT11': 16000000.00,
        'PAY_AMT12': 16000000.00
    }
    
    # Test với XGBoost model
    print("\n📊 Testing XGBoost model...")
    ml_service = MLService(model_name='XGBoost')
    
    results = []
    for i in range(5):
        result = ml_service.predict_default_risk(test_input)
        results.append((result.label, result.probability))
        print(f"  Run {i+1}: Label={result.label}, Probability={result.probability:.6f}")
    
    # Kiểm tra xem tất cả kết quả có giống nhau không
    all_same = all(r == results[0] for r in results)
    
    if all_same:
        print("\n✅ PASSED: Tất cả predictions đều giống nhau!")
        print(f"   → Model đang predict THỰC SỰ, không random")
        print(f"   → Kết quả nhất quán: Label={results[0][0]}, Prob={results[0][1]:.6f}")
    else:
        print("\n❌ FAILED: Predictions khác nhau!")
        print("   → Model có thể đang random hoặc có vấn đề")
    
    return all_same, results[0]

def test_different_inputs():
    """
    Test 2: Input khác nhau phải cho output khác nhau
    Nếu random thì có thể cho kết quả giống nhau
    """
    print("\n" + "="*60)
    print("TEST 2: DIFFERENT INPUTS → DIFFERENT OUTPUTS")
    print("="*60)
    
    ml_service = MLService(model_name='XGBoost')
    
    # Input 1: Khách hàng tốt (trả đúng hạn, limit cao)
    good_customer = {
        'LIMIT_BAL': 500000000.00,
        'SEX': 1, 'EDUCATION': 1, 'MARRIAGE': 1, 'AGE': 35,
        'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0, 'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
        'PAY_7': 0, 'PAY_8': 0, 'PAY_9': 0, 'PAY_10': 0, 'PAY_11': 0, 'PAY_12': 0,
        'BILL_AMT1': 50000000, 'BILL_AMT2': 50000000, 'BILL_AMT3': 50000000,
        'BILL_AMT4': 50000000, 'BILL_AMT5': 50000000, 'BILL_AMT6': 50000000,
        'BILL_AMT7': 50000000, 'BILL_AMT8': 50000000, 'BILL_AMT9': 50000000,
        'BILL_AMT10': 50000000, 'BILL_AMT11': 50000000, 'BILL_AMT12': 50000000,
        'PAY_AMT1': 50000000, 'PAY_AMT2': 50000000, 'PAY_AMT3': 50000000,
        'PAY_AMT4': 50000000, 'PAY_AMT5': 50000000, 'PAY_AMT6': 50000000,
        'PAY_AMT7': 50000000, 'PAY_AMT8': 50000000, 'PAY_AMT9': 50000000,
        'PAY_AMT10': 50000000, 'PAY_AMT11': 50000000, 'PAY_AMT12': 50000000
    }
    
    # Input 2: Khách hàng xấu (trễ nhiều tháng, limit thấp)
    bad_customer = {
        'LIMIT_BAL': 50000.00,
        'SEX': 2, 'EDUCATION': 4, 'MARRIAGE': 2, 'AGE': 25,
        'PAY_0': 3, 'PAY_2': 4, 'PAY_3': 5, 'PAY_4': 3, 'PAY_5': 4, 'PAY_6': 2,
        'PAY_7': 3, 'PAY_8': 2, 'PAY_9': 1, 'PAY_10': 2, 'PAY_11': 1, 'PAY_12': 2,
        'BILL_AMT1': 80000, 'BILL_AMT2': 90000, 'BILL_AMT3': 85000,
        'BILL_AMT4': 88000, 'BILL_AMT5': 92000, 'BILL_AMT6': 87000,
        'BILL_AMT7': 89000, 'BILL_AMT8': 91000, 'BILL_AMT9': 86000,
        'BILL_AMT10': 88000, 'BILL_AMT11': 90000, 'BILL_AMT12': 89000,
        'PAY_AMT1': 1000, 'PAY_AMT2': 1500, 'PAY_AMT3': 2000,
        'PAY_AMT4': 1000, 'PAY_AMT5': 1500, 'PAY_AMT6': 2000,
        'PAY_AMT7': 1000, 'PAY_AMT8': 1500, 'PAY_AMT9': 2000,
        'PAY_AMT10': 1000, 'PAY_AMT11': 1500, 'PAY_AMT12': 2000
    }
    
    result_good = ml_service.predict_default_risk(good_customer)
    result_bad = ml_service.predict_default_risk(bad_customer)
    
    print(f"\n👍 Khách hàng TỐT:")
    print(f"   Label: {result_good.label}, Probability: {result_good.probability:.6f}")
    
    print(f"\n👎 Khách hàng XẤU:")
    print(f"   Label: {result_bad.label}, Probability: {result_bad.probability:.6f}")
    
    # Khách xấu phải có xác suất vỡ nợ cao hơn khách tốt
    if result_bad.probability > result_good.probability:
        print("\n✅ PASSED: Khách xấu có xác suất vỡ nợ cao hơn!")
        print(f"   → Model học được patterns từ data")
        return True
    else:
        print("\n❌ FAILED: Logic không đúng!")
        print("   → Khách xấu phải có xác suất cao hơn khách tốt")
        return False

def test_model_info():
    """
    Test 3: Kiểm tra model có load đúng không
    """
    print("\n" + "="*60)
    print("TEST 3: MODEL LOADING INFO")
    print("="*60)
    
    ml_service = MLService(model_name='XGBoost')
    info = ml_service.get_model_info()
    
    print(f"\n📦 Model Info:")
    print(f"   Name: {info['model_name']}")
    print(f"   Path: {info['model_path']}")
    print(f"   Loaded: {info['is_loaded']}")
    
    predictor_info = ml_service.predictor.get_model_info()
    print(f"\n🔍 Predictor Info:")
    print(f"   Type: {predictor_info.get('type', 'N/A')}")
    print(f"   Loaded: {predictor_info.get('loaded', False)}")
    
    if info['is_loaded'] and predictor_info.get('loaded'):
        print("\n✅ PASSED: Model loaded successfully!")
        return True
    else:
        print("\n❌ FAILED: Model not loaded!")
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CREDIT RISK MODEL VERIFICATION TEST")
    print("="*60)
    
    # Run all tests
    test1_passed, consistent_result = test_prediction_consistency()
    test2_passed = test_different_inputs()
    test3_passed = test_model_info()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Consistency): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Logic): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Test 3 (Loading): {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("Hệ thống đang sử dụng model ĐÃ TRAIN, KHÔNG PHẢI RANDOM!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️ SOME TESTS FAILED!")
        print("="*60)
        print("Cần kiểm tra lại hệ thống!")
        print("="*60)
