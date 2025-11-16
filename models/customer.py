"""
Customer Model
Model cho dữ liệu khách hàng - Mở rộng lên 41 trường (12 tháng lịch sử)
"""
from typing import Optional, Dict


class Customer:
    """
    Lớp đại diện cho dữ liệu khách hàng - 41 features (12 tháng lịch sử)
    """
    
    def __init__(
        self,
        # Thông tin cá nhân
        customer_name: Optional[str] = None,
        customer_id_card: Optional[str] = None,
        LIMIT_BAL: float = 0.0,
        SEX: int = 1,
        EDUCATION: int = 2,
        MARRIAGE: int = 2,
        AGE: int = 30,
        
        # Lịch sử thanh toán - 12 tháng (PAY_0, PAY_2-12)
        PAY_0: int = 0,
        PAY_2: int = 0,
        PAY_3: int = 0,
        PAY_4: int = 0,
        PAY_5: int = 0,
        PAY_6: int = 0,
        PAY_7: int = 0,
        PAY_8: int = 0,
        PAY_9: int = 0,
        PAY_10: int = 0,
        PAY_11: int = 0,
        PAY_12: int = 0,
        
        # Số dư sao kê - 12 tháng (BILL_AMT1-12)
        BILL_AMT1: float = 0.0,
        BILL_AMT2: float = 0.0,
        BILL_AMT3: float = 0.0,
        BILL_AMT4: float = 0.0,
        BILL_AMT5: float = 0.0,
        BILL_AMT6: float = 0.0,
        BILL_AMT7: float = 0.0,
        BILL_AMT8: float = 0.0,
        BILL_AMT9: float = 0.0,
        BILL_AMT10: float = 0.0,
        BILL_AMT11: float = 0.0,
        BILL_AMT12: float = 0.0,
        
        # Số tiền thanh toán - 12 tháng (PAY_AMT1-12)
        PAY_AMT1: float = 0.0,
        PAY_AMT2: float = 0.0,
        PAY_AMT3: float = 0.0,
        PAY_AMT4: float = 0.0,
        PAY_AMT5: float = 0.0,
        PAY_AMT6: float = 0.0,
        PAY_AMT7: float = 0.0,
        PAY_AMT8: float = 0.0,
        PAY_AMT9: float = 0.0,
        PAY_AMT10: float = 0.0,
        PAY_AMT11: float = 0.0,
        PAY_AMT12: float = 0.0
    ):
        """
        Khởi tạo Customer với đầy đủ 41 trường (5 personal + 12*3 history)
        """
        # Metadata
        self.customer_name = customer_name
        self.customer_id_card = customer_id_card
        
        # Thông tin cá nhân
        self.LIMIT_BAL = LIMIT_BAL
        self.SEX = SEX
        self.EDUCATION = EDUCATION
        self.MARRIAGE = MARRIAGE
        self.AGE = AGE
        
        # Lịch sử thanh toán - 12 tháng
        self.PAY_0 = PAY_0
        self.PAY_2 = PAY_2
        self.PAY_3 = PAY_3
        self.PAY_4 = PAY_4
        self.PAY_5 = PAY_5
        self.PAY_6 = PAY_6
        self.PAY_7 = PAY_7
        self.PAY_8 = PAY_8
        self.PAY_9 = PAY_9
        self.PAY_10 = PAY_10
        self.PAY_11 = PAY_11
        self.PAY_12 = PAY_12
        
        # Số dư sao kê - 12 tháng
        self.BILL_AMT1 = BILL_AMT1
        self.BILL_AMT2 = BILL_AMT2
        self.BILL_AMT3 = BILL_AMT3
        self.BILL_AMT4 = BILL_AMT4
        self.BILL_AMT5 = BILL_AMT5
        self.BILL_AMT6 = BILL_AMT6
        self.BILL_AMT7 = BILL_AMT7
        self.BILL_AMT8 = BILL_AMT8
        self.BILL_AMT9 = BILL_AMT9
        self.BILL_AMT10 = BILL_AMT10
        self.BILL_AMT11 = BILL_AMT11
        self.BILL_AMT12 = BILL_AMT12
        
        # Số tiền thanh toán - 12 tháng
        self.PAY_AMT1 = PAY_AMT1
        self.PAY_AMT2 = PAY_AMT2
        self.PAY_AMT3 = PAY_AMT3
        self.PAY_AMT4 = PAY_AMT4
        self.PAY_AMT5 = PAY_AMT5
        self.PAY_AMT6 = PAY_AMT6
        self.PAY_AMT7 = PAY_AMT7
        self.PAY_AMT8 = PAY_AMT8
        self.PAY_AMT9 = PAY_AMT9
        self.PAY_AMT10 = PAY_AMT10
        self.PAY_AMT11 = PAY_AMT11
        self.PAY_AMT12 = PAY_AMT12
    
    def to_dict(self) -> Dict:
        """
        Chuyển Customer thành dict (41 features, không bao gồm metadata)
        
        Returns:
            Dict với 41 trường features (5 personal + 36 history)
        """
        return {
            'LIMIT_BAL': self.LIMIT_BAL,
            'SEX': self.SEX,
            'EDUCATION': self.EDUCATION,
            'MARRIAGE': self.MARRIAGE,
            'AGE': self.AGE,
            'PAY_0': self.PAY_0,
            'PAY_2': self.PAY_2,
            'PAY_3': self.PAY_3,
            'PAY_4': self.PAY_4,
            'PAY_5': self.PAY_5,
            'PAY_6': self.PAY_6,
            'PAY_7': self.PAY_7,
            'PAY_8': self.PAY_8,
            'PAY_9': self.PAY_9,
            'PAY_10': self.PAY_10,
            'PAY_11': self.PAY_11,
            'PAY_12': self.PAY_12,
            'BILL_AMT1': self.BILL_AMT1,
            'BILL_AMT2': self.BILL_AMT2,
            'BILL_AMT3': self.BILL_AMT3,
            'BILL_AMT4': self.BILL_AMT4,
            'BILL_AMT5': self.BILL_AMT5,
            'BILL_AMT6': self.BILL_AMT6,
            'BILL_AMT7': self.BILL_AMT7,
            'BILL_AMT8': self.BILL_AMT8,
            'BILL_AMT9': self.BILL_AMT9,
            'BILL_AMT10': self.BILL_AMT10,
            'BILL_AMT11': self.BILL_AMT11,
            'BILL_AMT12': self.BILL_AMT12,
            'PAY_AMT1': self.PAY_AMT1,
            'PAY_AMT2': self.PAY_AMT2,
            'PAY_AMT3': self.PAY_AMT3,
            'PAY_AMT4': self.PAY_AMT4,
            'PAY_AMT5': self.PAY_AMT5,
            'PAY_AMT6': self.PAY_AMT6,
            'PAY_AMT7': self.PAY_AMT7,
            'PAY_AMT8': self.PAY_AMT8,
            'PAY_AMT9': self.PAY_AMT9,
            'PAY_AMT10': self.PAY_AMT10,
            'PAY_AMT11': self.PAY_AMT11,
            'PAY_AMT12': self.PAY_AMT12
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Customer':
        """
        Tạo Customer từ dictionary
        
        Args:
            data: Dict chứa các trường customer
        
        Returns:
            Instance Customer
        """
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"Customer(name='{self.customer_name}', id_card='{self.customer_id_card}')"
