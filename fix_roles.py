import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='@Obama123', database='credit_risk_db')
c = conn.cursor()
c.execute('UPDATE user SET role="User" WHERE username="babyshark"')
c.execute('UPDATE user SET role="Admin" WHERE username="fathershark"')
conn.commit()
c.execute('SELECT username, role FROM user')
print('\nUser Roles:')
for username, role in c.fetchall():
    print(f'  {username:15s} - {role}')
conn.close()
print('\n✓ Roles fixed!')
