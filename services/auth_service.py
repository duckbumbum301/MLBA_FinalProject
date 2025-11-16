"""
Authentication Service
Service xử lý đăng nhập và mật khẩu
"""
import bcrypt
from typing import Optional
from database.connector import DatabaseConnector
from models.user import User


class AuthService:
    """
    Service quản lý authentication và authorization
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Khởi tạo AuthService
        
        Args:
            db_connector: Instance DatabaseConnector
        """
        self.db = db_connector
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash mật khẩu bằng bcrypt
        
        Args:
            password: Mật khẩu plain text
        
        Returns:
            Chuỗi hash
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Kiểm tra mật khẩu với hash
        
        Args:
            password: Mật khẩu plain text
            password_hash: Hash đã lưu
        
        Returns:
            True nếu khớp, False nếu không
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"✗ Lỗi verify password: {e}")
            return False
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Xác thực đăng nhập
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu plain text
        
        Returns:
            Instance User nếu thành công, None nếu thất bại
        """
        query = "SELECT id, username, password_hash, role, created_at FROM user WHERE username = %s"
        result = self.db.fetch_one(query, (username,))
        
        if not result:
            print(f"✗ Không tìm thấy user: {username}")
            return None
        
        user_id, username, password_hash, role, created_at = result
        
        # Verify password
        if not self.verify_password(password, password_hash):
            print(f"✗ Sai mật khẩu cho user: {username}")
            return None
        
        # Tạo User object
        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            created_at=created_at
        )
        
        print(f"✓ Đăng nhập thành công: {user}")
        return user
    
    def create_user(self, username: str, password: str, role: str = 'Secretary') -> bool:
        """
        Tạo user mới
        
        Args:
            username: Tên đăng nhập
            password: Mật khẩu plain text
            role: Vai trò (Admin/Technical/Secretary)
        
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Hash password
        password_hash = self.hash_password(password)
        
        # Insert vào database
        query = """
            INSERT INTO user (username, password_hash, role) 
            VALUES (%s, %s, %s)
        """
        success = self.db.execute_query(query, (username, password_hash, role))
        
        if success:
            print(f"✓ Đã tạo user: {username} ({role})")
        else:
            print(f"✗ Không thể tạo user: {username}")
        
        return success
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Đổi mật khẩu
        
        Args:
            username: Tên đăng nhập
            old_password: Mật khẩu cũ
            new_password: Mật khẩu mới
        
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Verify old password trước
        user = self.login(username, old_password)
        if not user:
            return False
        
        # Hash new password
        new_hash = self.hash_password(new_password)
        
        # Update database
        query = "UPDATE user SET password_hash = %s WHERE username = %s"
        success = self.db.execute_query(query, (new_hash, username))
        
        if success:
            print(f"✓ Đã đổi mật khẩu cho user: {username}")
        
        return success
