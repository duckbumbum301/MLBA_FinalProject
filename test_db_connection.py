"""
Test Database Connection
========================
Script kiểm tra kết nối MySQL cho Credit Risk System.

Chạy trước khi run ứng dụng chính.
"""

import sys
from config.database_config import DatabaseConfig
from database.connector import DatabaseConnector

def test_connection():
    """Test MySQL connection"""
    print("=" * 60)
    print("🔌 Testing MySQL Connection...")
    print("=" * 60)
    
    config = DatabaseConfig.default()
    print(f"\n📋 Connection Config:")
    print(f"   Host: {config.host}")
    print(f"   Port: {config.port}")
    print(f"   User: {config.user}")
    print(f"   Database: {config.database}")
    
    db = DatabaseConnector(config)
    
    # Test 1: Connection
    print(f"\n{'─' * 60}")
    print("Test 1: Basic Connection")
    print("─" * 60)
    
    if not db.connect():
        print("❌ FAILED: Cannot connect to MySQL server")
        print("\n💡 Troubleshooting:")
        print("   1. Check MySQL service is running:")
        print("      Get-Service MySQL*")
        print("   2. Verify password in config/database_config.py")
        print("   3. Check port 3306 is not blocked")
        return False
    
    print("✅ PASSED: Connected successfully")
    
    # Test 2: MySQL Version
    print(f"\n{'─' * 60}")
    print("Test 2: MySQL Version")
    print("─" * 60)
    
    try:
        result = db.fetch_one("SELECT VERSION()")
        version = result[0]
        print(f"✅ PASSED: MySQL version {version}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        db.close()
        return False
    
    # Test 3: Database Exists
    print(f"\n{'─' * 60}")
    print("Test 3: Database Exists")
    print("─" * 60)
    
    try:
        result = db.fetch_one(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (config.database,)
        )
        if result:
            print(f"✅ PASSED: Database '{config.database}' exists")
        else:
            print(f"❌ FAILED: Database '{config.database}' not found")
            print("\n💡 Create database:")
            print(f"   CREATE DATABASE {config.database};")
            db.close()
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        db.close()
        return False
    
    # Test 4: Tables Exist
    print(f"\n{'─' * 60}")
    print("Test 4: Required Tables")
    print("─" * 60)
    
    try:
        tables = db.fetch_all("SHOW TABLES")
        table_names = [t[0] for t in tables]
        
        required_tables = ['user', 'customers', 'predictions_log']
        
        all_exist = True
        for table in required_tables:
            if table in table_names:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} - NOT FOUND")
                all_exist = False
        
        if all_exist:
            print("\n✅ PASSED: All required tables exist")
        else:
            print("\n❌ FAILED: Some tables missing")
            print("\n💡 Run SQL scripts:")
            print("   source database/credit_scoring/user.sql;")
            print("   source database/credit_scoring/customers.sql;")
            print("   source database/credit_scoring/predictions_log.sql;")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        db.close()
        return False
    
    # Test 5: Demo Users
    print(f"\n{'─' * 60}")
    print("Test 5: Demo Users")
    print("─" * 60)
    
    try:
        users = db.fetch_all("SELECT username, role FROM user ORDER BY username")
        
        if len(users) == 0:
            print("❌ FAILED: No users found")
            print("\n💡 Run: source database/credit_scoring/user.sql;")
            db.close()
            return False
        
        print(f"   Found {len(users)} users:")
        for username, role in users:
            print(f"   ✅ {username:15s} ({role})")
        
        print("\n✅ PASSED: Demo users exist")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        db.close()
        return False
    
    # Test 6: Table Structure
    print(f"\n{'─' * 60}")
    print("Test 6: Customers Table Structure")
    print("─" * 60)
    
    try:
        columns = db.fetch_all("DESCRIBE customers")
        column_names = [col[0] for col in columns]
        
        # Check critical columns
        required_columns = [
            'customer_id', 'LIMIT_BAL', 'SEX', 'EDUCATION', 
            'MARRIAGE', 'AGE', 'PAY_0', 'PAY_2', 'PAY_3', 
            'PAY_4', 'PAY_5', 'PAY_6'
        ]
        
        missing = [col for col in required_columns if col not in column_names]
        
        if missing:
            print(f"❌ FAILED: Missing columns: {', '.join(missing)}")
            db.close()
            return False
        
        print(f"   Total columns: {len(column_names)}")
        print(f"   ✅ All critical columns exist")
        print("\n✅ PASSED: Table structure correct")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        db.close()
        return False
    
    db.close()
    
    # Final Summary
    print(f"\n{'=' * 60}")
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✅ MySQL database is ready for Credit Risk System")
    print("\n📌 Next Steps:")
    print("   1. Train models: python ml/train_models.py")
    print("   2. Run application: python -m tests.test_app")
    print("   3. Login with: babyshark / 123")
    
    return True

if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
