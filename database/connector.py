"""
Database Connector
Lớp kết nối và thao tác với MySQL database
"""
import mysql.connector
from mysql.connector import Error
from typing import List, Tuple, Optional, Any
from config.database_config import DatabaseConfig


class DatabaseConnector:
    """
    Lớp quản lý kết nối và truy vấn MySQL database
    Sử dụng parameterized queries để tránh SQL injection
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Khởi tạo connector với cấu hình
        
        Args:
            config: Instance DatabaseConfig
        """
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Tạo kết nối tới MySQL database
        
        Returns:
            True nếu kết nối thành công, False nếu thất bại
        """
        try:
            self.connection = mysql.connector.connect(**self.config.to_dict())
            self.cursor = self.connection.cursor()
            print(f"✓ Đã kết nối tới database: {self.config.database}")
            return True
        except Error as e:
            print(f"✗ Lỗi kết nối database: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Thực thi câu lệnh INSERT/UPDATE/DELETE và tự động commit
        
        Args:
            query: Câu SQL query (dùng %s cho placeholder)
            params: Tuple các tham số cho query
        
        Returns:
            True nếu thành công, False nếu thất bại
        """
        if not self.connection or not self.cursor:
            print("✗ Chưa có kết nối database")
            return False
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Lỗi execute query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Thực thi SELECT query và trả về tất cả kết quả
        
        Args:
            query: Câu SQL SELECT query
            params: Tuple các tham số cho query
        
        Returns:
            List các tuple kết quả, hoặc list rỗng nếu lỗi
        """
        if not self.connection or not self.cursor:
            print("✗ Chưa có kết nối database")
            return []
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except Error as e:
            print(f"✗ Lỗi fetch_all: {e}")
            return []
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """
        Thực thi SELECT query và trả về 1 kết quả duy nhất
        
        Args:
            query: Câu SQL SELECT query
            params: Tuple các tham số cho query
        
        Returns:
            Tuple kết quả hoặc None nếu không có/lỗi
        """
        if not self.connection or not self.cursor:
            print("✗ Chưa có kết nối database")
            return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result
        except Error as e:
            print(f"✗ Lỗi fetch_one: {e}")
            return None
    
    def close(self):
        """
        Đóng kết nối database
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✓ Đã đóng kết nối database")
    
    def __enter__(self):
        """Context manager enter"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
