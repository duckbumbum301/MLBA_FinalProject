"""
User Model
Model cho tài khoản người dùng hệ thống (2 roles: User/Admin)
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
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        is_active: bool = True
    ):
        """
        Khởi tạo User
        
        Args:
            id: ID user trong database
            username: Tên đăng nhập
            password_hash: Hash của mật khẩu (bcrypt)
            role: Vai trò (User/Admin)
            full_name: Họ tên đầy đủ
            email: Email liên hệ
            created_at: Thời điểm tạo tài khoản
            last_login: Thời điểm đăng nhập gần nhất
            is_active: Trạng thái active
        """
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
        self.is_active = is_active
    
    def is_admin(self) -> bool:
        """Kiểm tra user có phải Admin không"""
        return self.role == 'Admin'
    
    def is_user(self) -> bool:
        """Kiểm tra user có phải User không"""
        return self.role == 'User'
    
    def has_access_to_prediction(self) -> bool:
        """Kiểm tra quyền truy cập tab Prediction (tất cả users)"""
        return True
    
    def has_access_to_reports(self) -> bool:
        """Kiểm tra quyền truy cập tab Reports (tất cả users)"""
        return True
    
    def has_access_to_ai_assistant(self) -> bool:
        """Kiểm tra quyền truy cập tab AI Assistant (tất cả users)"""
        return True
    
    def has_access_to_model_management(self) -> bool:
        """Kiểm tra quyền truy cập tab Model Management (chỉ Admin)"""
        return self.is_admin()
    
    def has_access_to_system_management(self) -> bool:
        """Kiểm tra quyền truy cập tab System Management (chỉ Admin)"""
        return self.is_admin()
    
    def can_select_model(self) -> bool:
        """Kiểm tra quyền chọn model (chỉ Admin)"""
        return self.is_admin()
    
    def can_train_model(self) -> bool:
        """Kiểm tra quyền train model (chỉ Admin)"""
        return self.is_admin()
    
    def can_view_all_predictions(self) -> bool:
        """Kiểm tra quyền xem predictions của tất cả users (chỉ Admin)"""
        return self.is_admin()
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', role='{self.role}')"
    
    def __str__(self) -> str:
        name = self.full_name or self.username
        return f"{name} ({self.role})"
