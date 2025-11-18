"""
Generate 200 fake customers với data random hợp lý
"""
import sys
import random
import numpy as np
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from database.connector import DatabaseConnector
from models.customer import Customer

# Tên Việt Nam
first_names = ['An','Bình','Chi','Dục','Huy','Khánh','Lan','Minh','Nam','Phong',
               'Quang','Sơn','Tuấn','Việt','Yên','Anh','Trang','Linh','Hoa','Ngọc']
last_names = ['Nguyễn','Trần','Lê','Phạm','Hoàng','Huỳnh','Phan','Vũ','Võ','Đặng',
              'Bùi','Đỗ','Ngô','Dương','Lý']

def generate_customer_data():
    """Tạo 1 customer với data random hợp lý"""
    # Thông tin cá nhân
    limit_bal = random.choice([10000, 20000, 30000, 50000, 80000, 100000, 150000, 200000, 300000, 500000])
    sex = random.randint(1, 2)
    education = random.choices([1,2,3,4], weights=[10, 50, 30, 10])[0]  # Đa số đại học
    marriage = random.choices([1,2,3], weights=[40, 50, 10])[0]  # Đa số độc thân/kết hôn
    age = random.randint(22, 60)
    
    # Tạo tên và CMND
    full_name = f"{random.choice(last_names)} {random.choice(first_names)}"
    citizen_id = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    # Logic payment history: Người trẻ/hạn mức thấp → Dễ trễ hơn
    risk_factor = 0.3 if age < 30 else 0.1
    risk_factor += 0.2 if limit_bal < 50000 else 0
    
    pay_history = []
    for _ in range(12):
        if random.random() < risk_factor:
            # Có risk → Trễ
            pay_history.append(random.choices(
                [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                weights=[5, 20, 30, 15, 10, 8, 5, 3, 2, 1, 0.5, 0.5]
            )[0])
        else:
            # Không risk → Trả đúng hạn
            pay_history.append(random.choices([-1, 0], weights=[30, 70])[0])
    
    # Bill amounts: 10-80% hạn mức
    bill_amts = [random.randint(int(limit_bal*0.1), int(limit_bal*0.8)) for _ in range(12)]
    
    # Pay amounts: 5-100% bill amount
    pay_amts = []
    for bill in bill_amts:
        if bill > 0:
            pay_amts.append(random.randint(int(bill*0.05), bill))
        else:
            pay_amts.append(0)
    
    return Customer(
        customer_name=full_name,
        customer_id_card=citizen_id,
        LIMIT_BAL=limit_bal,
        SEX=sex,
        EDUCATION=education,
        MARRIAGE=marriage,
        AGE=age,
        PAY_0=pay_history[0], PAY_2=pay_history[1], PAY_3=pay_history[2],
        PAY_4=pay_history[3], PAY_5=pay_history[4], PAY_6=pay_history[5],
        PAY_7=pay_history[6], PAY_8=pay_history[7], PAY_9=pay_history[8],
        PAY_10=pay_history[9], PAY_11=pay_history[10], PAY_12=pay_history[11],
        BILL_AMT1=bill_amts[0], BILL_AMT2=bill_amts[1], BILL_AMT3=bill_amts[2],
        BILL_AMT4=bill_amts[3], BILL_AMT5=bill_amts[4], BILL_AMT6=bill_amts[5],
        BILL_AMT7=bill_amts[6], BILL_AMT8=bill_amts[7], BILL_AMT9=bill_amts[8],
        BILL_AMT10=bill_amts[9], BILL_AMT11=bill_amts[10], BILL_AMT12=bill_amts[11],
        PAY_AMT1=pay_amts[0], PAY_AMT2=pay_amts[1], PAY_AMT3=pay_amts[2],
        PAY_AMT4=pay_amts[3], PAY_AMT5=pay_amts[4], PAY_AMT6=pay_amts[5],
        PAY_AMT7=pay_amts[6], PAY_AMT8=pay_amts[7], PAY_AMT9=pay_amts[8],
        PAY_AMT10=pay_amts[9], PAY_AMT11=pay_amts[10], PAY_AMT12=pay_amts[11]
    )

if __name__ == '__main__':
    print("="*60)
    print("TẠO 200 KHÁCH HÀNG ẢO")
    print("="*60)
    
    from config.database_config import DatabaseConfig
    
    config = DatabaseConfig()
    db = DatabaseConnector(config)
    db.connect()
    
    from services.query_service import QueryService
    query_service = QueryService(db)
    
    success = 0
    for i in range(200):
        try:
            customer = generate_customer_data()
            customer_id = query_service.save_customer(customer)
            success += 1
            if (i+1) % 20 == 0:
                print(f"✓ Đã tạo {i+1}/200 khách hàng...")
        except Exception as e:
            print(f"✗ Lỗi customer {i+1}: {e}")
    
    db.close()
    print("="*60)
    print(f"✓ HOÀN THÀNH! Đã tạo {success}/200 khách hàng")
    print("="*60)
