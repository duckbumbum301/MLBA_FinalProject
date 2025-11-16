"""
Generate Password Hash
Tạo bcrypt hash cho password "123"
"""
import bcrypt

password = "123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print(f"Password: {password}")
print(f"Hash: {hashed.decode('utf-8')}")

# Test verify
verify = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"Verify: {verify}")
