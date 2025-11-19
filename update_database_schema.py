"""
Script to update database with new tables for 2-role system
Run this to apply all schema changes
"""
import mysql.connector
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config.database_config import DatabaseConfig

def main():
    print("\n" + "="*60)
    print("DATABASE SCHEMA UPDATE - 2 ROLES + ML REGISTRY")
    print("="*60)
    
    # Connect
    config = DatabaseConfig.default()
    conn = mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database
    )
    cursor = conn.cursor()
    
    print("\n✓ Connected to database:", config.database)
    
    # Read and execute SQL files
    sql_files = [
        'database\\credit_scoring\\user.sql',
        'database\\credit_scoring\\customers.sql',
        'database\\credit_scoring\\model_registry.sql',
        'database\\credit_scoring\\customer_clusters.sql',
        'database\\credit_scoring\\data_quality_log.sql',
        'database\\credit_scoring\\ai_chat_history.sql',
        'database\\credit_scoring\\predictions_log.sql',
        'MLBA_FinalProject\\update_passwords.sql'
    ]
    
    for sql_file in sql_files:
        filepath = project_root / sql_file
        if not filepath.exists():
            print(f"⚠ Skip {sql_file} (not found)")
            continue
        
        print(f"\n▶ Executing {sql_file}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and execute
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for statement in statements:
            if statement.startswith('--') or not statement:
                continue
            try:
                if statement.strip().upper().startswith('SELECT'):
                    cursor.execute(statement)
                    _ = cursor.fetchall()
                else:
                    cursor.execute(statement)
                    conn.commit()
            except Exception as e:
                print(f"  ⚠ Warning: {e}")
        
        print(f"  ✓ Done")
    # Ensure threshold audit table and column
    try:
        print("\n▶ Ensuring model_thresholds table...")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_thresholds (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(64) NOT NULL,
                threshold DECIMAL(5,4) NOT NULL,
                updated_by VARCHAR(64),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_model (model_name),
                INDEX idx_created (created_at)
            )
            """
        )
        conn.commit()
        print("  ✓ model_thresholds ready")
    except Exception as e:
        print(f"  ⚠ model_thresholds failed: {e}")
    try:
        print("\n▶ Ensuring model_registry.threshold column...")
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = %s AND table_name = 'model_registry' AND column_name = 'threshold'
            """,
            (config.database,)
        )
        exists = cursor.fetchone()[0] > 0
        if not exists:
            cursor.execute("ALTER TABLE model_registry ADD COLUMN threshold DECIMAL(5,4) NULL")
            conn.commit()
            print("  ✓ Added model_registry.threshold")
        else:
            print("  ✓ model_registry.threshold exists")
    except Exception as e:
        print(f"  ⚠ threshold column check failed: {e}")
    
    # Verify tables
    print("\n" + "-"*60)
    print("Verifying tables...")
    print("-"*60)
    
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['user', 'customers', 'predictions_log', 'model_registry', 
                       'customer_clusters', 'data_quality_log', 'ai_chat_history', 'model_thresholds']
    
    for table in expected_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table:25s} - {count:5d} rows")
        else:
            print(f"✗ {table:25s} - NOT FOUND")
    
    # Show user roles
    print("\n" + "-"*60)
    print("User Accounts:")
    print("-"*60)
    
    try:
        cursor.execute("SELECT id, username, role, full_name FROM user")
        for user_id, username, role, full_name in cursor.fetchall():
            print(f"  {user_id}. {username:15s} - {role:10s} - {full_name or 'N/A'}")
    except Exception as e:
        print(f"  ⚠ Could not fetch users: {e}")
        # Try without full_name
        try:
            cursor.execute("SELECT id, username, role FROM user")
            for user_id, username, role in cursor.fetchall():
                print(f"  {user_id}. {username:15s} - {role:10s}")
        except:
            pass
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✓ DATABASE UPDATE COMPLETED!")
    print("="*60)
    print("\nLogin credentials (password: 123):")
    print("  • babyshark   (User)")
    print("  • fathershark (Admin)")
    print("  • momshark    (User)")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
