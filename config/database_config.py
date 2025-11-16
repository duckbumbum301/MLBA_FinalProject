"""
Database Configuration
Cấu hình kết nối MySQL cho ứng dụng Credit Risk Scoring
"""
from typing import Dict


class DatabaseConfig:
    """
    Lớp cấu hình database MySQL
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 3306,
        user: str = 'root',
        password: str = '@Obama123',
        database: str = 'credit_risk_db'
    ):
        """
        Khởi tạo cấu hình database
        
        Args:
            host: MySQL host address
            port: MySQL port (mặc định 3306)
            user: MySQL username
            password: MySQL password
            database: Tên database
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    
    def to_dict(self) -> Dict[str, any]:
        """
        Chuyển cấu hình thành dictionary để dùng cho mysql.connector
        
        Returns:
            Dict chứa các thông số kết nối
        """
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    
    @classmethod
    def default(cls) -> 'DatabaseConfig':
        """
        Trả về cấu hình mặc định
        
        Returns:
            Instance DatabaseConfig với các giá trị mặc định
        """
        return cls()
