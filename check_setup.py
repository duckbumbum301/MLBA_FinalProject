"""
Check Setup Script
Kiểm tra các yêu cầu trước khi chạy ứng dụng
"""
import sys
from pathlib import Path

def check_requirements():
    """Kiểm tra các requirements cơ bản"""
    
    print("="*60)
    print("CREDIT RISK SYSTEM - SETUP CHECKER")
    print("="*60)
    
    errors = []
    warnings = []
    
    # 1. Check Python version
    print("\n1️⃣ Checking Python version...")
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 8:
        print(f"   ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        errors.append(f"Python version {py_version.major}.{py_version.minor} < 3.8")
    
    # 2. Check required packages
    print("\n2️⃣ Checking required packages...")
    required_packages = [
        'PyQt6',
        'mysql.connector',
        'pandas',
        'numpy',
        'sklearn',
        'lightgbm',
        'xgboost',
        'matplotlib',
        'bcrypt',
        'joblib'
    ]
    
    for package in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
            else:
                __import__(package.lower().replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            errors.append(f"Missing package: {package}")
            print(f"   ❌ {package}")
    
    # 3. Check data file
    print("\n3️⃣ Checking dataset...")
    data_path = Path(__file__).parent / 'UCI_Credit_Card.csv'
    if data_path.exists():
        print(f"   ✅ UCI_Credit_Card.csv found")
    else:
        errors.append("UCI_Credit_Card.csv not found")
        print(f"   ❌ UCI_Credit_Card.csv not found")
    
    # 4. Check ML models
    print("\n4️⃣ Checking ML models...")
    models_dir = Path(__file__).parent / 'outputs' / 'models'
    model_files = ['xgb_model.pkl', 'lgbm_model.pkl', 'lr_cal_model.pkl']
    
    missing_models = []
    for model_file in model_files:
        model_path = models_dir / model_file
        if model_path.exists():
            print(f"   ✅ {model_file}")
        else:
            missing_models.append(model_file)
            print(f"   ⚠️  {model_file} not found")
    
    if missing_models:
        warnings.append(f"Missing models: {', '.join(missing_models)}")
        print(f"\n   ⚠️  Run: python ml/train_models.py")
    
    # 5. Check database config
    print("\n5️⃣ Checking database configuration...")
    try:
        from config.database_config import DatabaseConfig
        db_config = DatabaseConfig.default()
        print(f"   ✅ Database config loaded")
        print(f"      Host: {db_config.host}")
        print(f"      Database: {db_config.database}")
        print(f"      User: {db_config.user}")
    except Exception as e:
        errors.append(f"Database config error: {e}")
        print(f"   ❌ Error: {e}")
    
    # 6. Test MySQL connection (optional)
    print("\n6️⃣ Testing MySQL connection...")
    try:
        from database.connector import DatabaseConnector
        from config.database_config import DatabaseConfig
        
        config = DatabaseConfig.default()
        db = DatabaseConnector(config)
        
        if db.connect():
            print(f"   ✅ MySQL connection successful")
            
            # Check if tables exist
            tables = db.fetch_all("SHOW TABLES")
            if tables:
                print(f"   ✅ Found {len(tables)} tables")
                for table in tables:
                    print(f"      - {table[0]}")
            else:
                warnings.append("No tables found. Run SQL setup scripts.")
                print(f"   ⚠️  No tables found")
            
            db.close()
        else:
            errors.append("Cannot connect to MySQL")
            print(f"   ❌ Cannot connect to MySQL")
    except Exception as e:
        errors.append(f"MySQL connection error: {e}")
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"   - {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nYou can run the application:")
        print("   python -m tests.test_app")
    elif not errors:
        print("\n⚠️  SOME WARNINGS - App may still work")
        print("\nYou can try running:")
        print("   python -m tests.test_app")
    else:
        print("\n❌ PLEASE FIX ERRORS BEFORE RUNNING APP")
        print("\nSetup instructions:")
        print("   1. Install packages: pip install -r requirements.txt")
        print("   2. Setup MySQL database (see README.md)")
        print("   3. Train models: python ml/train_models.py")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    check_requirements()
