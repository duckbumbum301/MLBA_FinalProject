"""
Debug Login - Test authentication
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
from services.auth_service import AuthService

def main():
    print("\n" + "="*60)
    print("DEBUG LOGIN")
    print("="*60)
    
    # Connect database
    db_config = DatabaseConfig.default()
    print(f"\nDatabase Config:")
    print(f"  Host: {db_config.host}:{db_config.port}")
    print(f"  Database: {db_config.database}")
    print(f"  User: {db_config.user}")
    
    db = DatabaseConnector(db_config)
    success = db.connect()
    
    if not success:
        print("\n✗ FAILED: Cannot connect to database")
        return
    
    print("\n✓ Database connected")
    
    # Test users
    auth_service = AuthService(db)
    
    test_users = [
        ("babyshark", "123"),
        ("fathershark", "123"),
        ("momshark", "123")
    ]
    
    print("\n" + "-"*60)
    print("Testing Login:")
    print("-"*60)
    
    for username, password in test_users:
        print(f"\nTesting: {username} / {password}")
        user = auth_service.login(username, password)
        
        if user:
            print(f"  ✓ SUCCESS - Role: {user.role}")
        else:
            print(f"  ✗ FAILED")
    
    # Show actual data in database
    print("\n" + "-"*60)
    print("Users in Database:")
    print("-"*60)
    
    query = "SELECT id, username, role, LEFT(password_hash, 30) as hash_preview FROM user"
    results = db.fetch_all(query)
    
    if results:
        for row in results:
            user_id, username, role, hash_preview = row
            print(f"  ID: {user_id:2d} | User: {username:15s} | Role: {role:10s} | Hash: {hash_preview}...")
    else:
        print("  No users found!")
    
    # Close connection
    db.close()
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
