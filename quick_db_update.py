"""
Quick Database Update - Apply 2-role system
"""
import mysql.connector

# Connect
conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='@Obama123',
    database='credit_risk_db'
)

cursor = conn.cursor()

print("="*60)
print("DATABASE UPDATE - 2 ROLES SYSTEM")
print("="*60)

# 1. Update user table - add new columns
print("\n1. Updating user table...")
try:
    cursor.execute("ALTER TABLE user ADD COLUMN full_name VARCHAR(100)")
    print("  ✓ Added full_name column")
except:
    print("  - full_name column already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(100)")
    print("  ✓ Added email column")
except:
    print("  - email column already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN last_login DATETIME")
    print("  ✓ Added last_login column")
except:
    print("  - last_login column already exists")

try:
    cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
    print("  ✓ Added is_active column")
except:
    print("  - is_active column already exists")

# 2. Update roles to 2-role system
print("\n2. Converting to 2-role system (User/Admin)...")
try:
    # First, modify ENUM to accept both old and new values
    cursor.execute("ALTER TABLE user MODIFY COLUMN role ENUM('Admin', 'Technical', 'Secretary', 'User') NOT NULL DEFAULT 'User'")
    print("  ✓ Extended role ENUM")
except Exception as e:
    print(f"  ⚠ Could not extend ENUM: {e}")

# Update role values
cursor.execute("UPDATE user SET role = 'User' WHERE role = 'Secretary'")
cursor.execute("UPDATE user SET role = 'User' WHERE role = 'Technical'")
# Admin stays Admin

# Now restrict to 2 roles only
try:
    cursor.execute("ALTER TABLE user MODIFY COLUMN role ENUM('User', 'Admin') NOT NULL DEFAULT 'User'")
    print("  ✓ Set role to 2-role system (User/Admin)")
except Exception as e:
    print(f"  ⚠ Could not restrict ENUM: {e}")

cursor.execute("UPDATE user SET full_name = 'Nhân viên A' WHERE username = 'babyshark'")
cursor.execute("UPDATE user SET full_name = 'Quản trị viên' WHERE username = 'fathershark'")
cursor.execute("UPDATE user SET full_name = 'Nhân viên B' WHERE username = 'momshark'")
conn.commit()
print("  ✓ Updated user data")

# 3. Create model_registry table
print("\n3. Creating model_registry table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS model_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(50) UNIQUE NOT NULL,
    model_type ENUM('Single', 'Ensemble') DEFAULT 'Single',
    algorithm VARCHAR(50),
    version VARCHAR(20) DEFAULT '1.0',
    auc_score DECIMAL(5,4),
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    is_active BOOLEAN DEFAULT FALSE,
    training_time INT,
    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    trained_by VARCHAR(50),
    model_path VARCHAR(255),
    model_size_mb DECIMAL(10,2),
    INDEX idx_active (is_active),
    INDEX idx_auc (auc_score DESC)
)
""")
conn.commit()
print("  ✓ Created model_registry")

# Insert existing models
cursor.execute("""
INSERT IGNORE INTO model_registry 
(model_name, model_type, algorithm, auc_score, accuracy, precision_score, 
 recall_score, f1_score, is_active, model_path) 
VALUES
('XGBoost', 'Single', 'XGBoost', 0.7604, 0.8200, 0.7800, 0.8500, 0.8100, TRUE, 'outputs/models/xgb_model.pkl'),
('LightGBM', 'Single', 'LightGBM', 0.7811, 0.8300, 0.7900, 0.8600, 0.8200, FALSE, 'outputs/models/lgbm_model.pkl'),
('LogisticRegression', 'Single', 'LogisticRegression', 0.7099, 0.7500, 0.7200, 0.7800, 0.7400, FALSE, 'outputs/models/lr_cal_model.pkl')
""")
conn.commit()
print("  ✓ Inserted 3 existing models")

# 4. Create customer_clusters table
print("\n4. Creating customer_clusters table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS customer_clusters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    cluster_id INT,
    risk_level ENUM('Low', 'Medium', 'High', 'Critical'),
    cluster_center_distance DECIMAL(10,4),
    clustered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (customer_id),
    INDEX idx_cluster (cluster_id),
    INDEX idx_risk (risk_level)
)
""")
conn.commit()
print("  ✓ Created customer_clusters")

# 5. Create data_quality_log table
print("\n5. Creating data_quality_log table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS data_quality_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT,
    record_type ENUM('Customer', 'Prediction'),
    issue_type VARCHAR(100),
    severity ENUM('Low', 'Medium', 'High'),
    detection_method VARCHAR(50),
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    detected_by VARCHAR(50),
    action_taken ENUM('Deleted', 'Fixed', 'Ignored', 'Pending') DEFAULT 'Pending',
    action_at DATETIME,
    action_by VARCHAR(50),
    notes TEXT,
    INDEX idx_record (record_id),
    INDEX idx_issue (issue_type),
    INDEX idx_status (action_taken)
)
""")
conn.commit()
print("  ✓ Created data_quality_log")

# 6. Create ai_chat_history table
print("\n6. Creating ai_chat_history table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    context_type VARCHAR(50),
    context_data JSON,
    user_message TEXT,
    ai_response TEXT,
    response_time_ms INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at DESC)
)
""")
conn.commit()
print("  ✓ Created ai_chat_history")

# 7. Update predictions_log table
print("\n7. Updating predictions_log table...")
try:
    cursor.execute("ALTER TABLE predictions_log ADD COLUMN user_id INT")
    print("  ✓ Added user_id column")
except:
    print("  - user_id column already exists")

try:
    cursor.execute("ALTER TABLE predictions_log ADD COLUMN model_version VARCHAR(50) DEFAULT 'v1.0'")
    print("  ✓ Added model_version column")
except:
    print("  - model_version column already exists")

try:
    cursor.execute("ALTER TABLE predictions_log ADD COLUMN confidence_score DECIMAL(5,4)")
    print("  ✓ Added confidence_score column")
except:
    print("  - confidence_score column already exists")

try:
    cursor.execute("ALTER TABLE predictions_log ADD COLUMN cluster_id INT")
    print("  ✓ Added cluster_id column")
except:
    print("  - cluster_id column already exists")

conn.commit()

# Verify
print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

cursor.execute("SHOW TABLES")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nTotal tables: {len(tables)}")

for table in ['user', 'model_registry', 'customer_clusters', 'data_quality_log', 'ai_chat_history']:
    if table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"✓ {table:25s} - {count:5d} rows")

print("\n" + "-"*60)
print("User Accounts:")
print("-"*60)
cursor.execute("SELECT username, role, full_name FROM user")
for username, role, full_name in cursor.fetchall():
    print(f"  • {username:15s} - {role:10s} - {full_name or 'N/A'}")

print("\n" + "-"*60)
print("Models:")
print("-"*60)
cursor.execute("SELECT model_name, algorithm, auc_score, is_active FROM model_registry")
for model_name, algorithm, auc, is_active in cursor.fetchall():
    status = "✅ ACTIVE" if is_active else "⬜"
    print(f"  {status} {model_name:20s} (AUC: {auc:.4f})")

cursor.close()
conn.close()

print("\n" + "="*60)
print("✓ DATABASE UPDATE COMPLETED!")
print("="*60)
print("\nLogin with:")
print("  Admin:  fathershark / 123")
print("  User:   babyshark / 123")
print("  User:   momshark / 123")
print("="*60)
