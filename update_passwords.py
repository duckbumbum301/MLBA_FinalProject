"""
Update User Passwords
Cập nhật password hash cho 3 demo users
"""
import os
import mysql.connector
from mysql.connector import Error

HOST = 'localhost'
USER = 'root'
PASSWORD = '@Obama123'
DATABASE = 'credit_risk_db'

def ensure_database():
    try:
        c = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
        c.close()
        return True
    except Error as e:
        if getattr(e, 'errno', None) == 1049:
            t = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
            cur = t.cursor()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DATABASE}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            t.close()
            return True
        raise

def ensure_user_table():
    c = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cur = c.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s AND table_name='user'",
        (DATABASE,)
    )
    exists = cur.fetchone()[0] > 0
    if not exists:
        sql_path = os.path.join('database', 'credit_scoring', 'user.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            script = f.read()
        for _ in cur.execute(script, multi=True):
            pass
        c.commit()
    cur.close()
    c.close()

def main():
    ensure_database()
    ensure_user_table()
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = conn.cursor()
    new_hash = '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm'
    query = """
    UPDATE user 
    SET password_hash = %s 
    WHERE username IN ('babyshark', 'fathershark', 'momshark')
    """
    cursor.execute(query, (new_hash,))
    conn.commit()
    print(f"✓ Updated {cursor.rowcount} users")
    cursor.execute("SELECT id, username, role FROM user")
    results = cursor.fetchall()
    print("\nUsers in database:")
    for user_id, username, role in results:
        print(f"  {user_id}. {username:15s} - {role:10s} - Password: 123")
    cursor.close()
    conn.close()
    print("\n✓ Done!")

if __name__ == '__main__':
    main()
