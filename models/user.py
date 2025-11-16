"""
User Model
Model cho tài khoản người dùng hệ thống
"""
from datetime import datetime
from typing import Optional


class User:
    """
    Lớp đại diện cho người dùng hệ thống
    """
    
    def __init__(
        self,
        id: int,
        username: str,
        password_hash: str,
        role: str,
        created_at: Optional[datetime] = None
    ):
        """
        Khởi tạo User
        
        Args:
            id: ID user trong database
            username: Tên đăng nhập
            password_hash: Hash của mật khẩu (bcrypt)
            role: Vai trò (Admin/Technical/Secretary)
            created_at: Thời điểm tạo tài khoản
        """
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now()
    
    def is_admin(self) -> bool:
        """Kiểm tra user có phải Admin không"""
        return self.role == 'Admin'
    
    def is_technical(self) -> bool:
        """Kiểm tra user có phải Technical không"""
        return self.role == 'Technical'
    
    def is_secretary(self) -> bool:
        """Kiểm tra user có phải Secretary không"""
        return self.role == 'Secretary'
    
    def has_access_to_prediction(self) -> bool:
        """Kiểm tra quyền truy cập tab Prediction"""
        return True  # Tất cả roles đều có quyền
    
    def has_access_to_dashboard(self) -> bool:
        """Kiểm tra quyền truy cập tab Dashboard"""
        return self.role in ['Admin', 'Technical']
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', role='{self.role}')"
    
    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
