"""
Update User Passwords
Cập nhật password hash cho 3 demo users
"""
import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='@Obama123',
    database='credit_risk_db'
)

cursor = conn.cursor()

# New hash for password "123"
new_hash = '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm'

# Update all 3 users
query = """
UPDATE user 
SET password_hash = %s 
WHERE username IN ('babyshark', 'fathershark', 'momshark')
"""

cursor.execute(query, (new_hash,))
conn.commit()

print(f"✓ Updated {cursor.rowcount} users")

# Verify
cursor.execute("SELECT id, username, role FROM user")
results = cursor.fetchall()

print("\nUsers in database:")
for user_id, username, role in results:
    print(f"  {user_id}. {username:15s} - {role:10s} - Password: 123")

cursor.close()
conn.close()
print("\n✓ Done!")
