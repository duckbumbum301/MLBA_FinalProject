"""
Test Search Customer by CMND
"""
from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
from services.query_service import QueryService

# Setup
config = DatabaseConfig()
db = DatabaseConnector(config)
db.connect()

query_service = QueryService(db)

# Lấy 5 khách hàng mẫu
print("="*60)
print("5 KHÁCH HÀNG MẪU")
print("="*60)

result = db.fetch_all("SELECT customer_name, customer_id_card, LIMIT_BAL, AGE FROM customers LIMIT 5")

for row in result:
    print(f"Tên: {row[0]:<20} CMND: {row[1]:<15} Hạn mức: {row[2]:>10.0f} NT$ ({row[2]*800:>12,.0f} VND)  Tuổi: {row[3]}")

print()
print("="*60)
print("TEST TÌM KIẾM THEO CMND")
print("="*60)

# Test tìm kiếm khách hàng đầu tiên
test_cmnd = result[0][1]
print(f"Tìm kiếm CMND: {test_cmnd}")

customer = query_service.get_customer_by_cmnd(test_cmnd)

if customer:
    print(f"✓ Tìm thấy: {customer.customer_name}")
    print(f"  - CMND: {customer.customer_id_card}")
    print(f"  - Hạn mức: {customer.LIMIT_BAL:,.0f} NT$ = {customer.LIMIT_BAL*800:,.0f} VND")
    print(f"  - Tuổi: {customer.AGE}")
    print(f"  - Giới tính: {'Nam' if customer.SEX == 1 else 'Nữ'}")
    print(f"  - PAY_0 (tháng gần nhất): {customer.PAY_0}")
    print(f"  - BILL_AMT1: {customer.BILL_AMT1:,.0f} NT$ = {customer.BILL_AMT1*800:,.0f} VND")
    print(f"  - PAY_AMT1: {customer.PAY_AMT1:,.0f} NT$ = {customer.PAY_AMT1*800:,.0f} VND")
else:
    print("✗ Không tìm thấy khách hàng")

print()
print("="*60)
print("TEST CHUYỂN ĐỔI TIỀN TỆ")
print("="*60)

test_amounts = [10000, 50000, 100000, 500000]
for nt in test_amounts:
    vnd = nt * 800
    print(f"{nt:>10,} NT$ = {vnd:>15,} VND")

db.close()
print()
print("✓ Hoàn thành test!")
