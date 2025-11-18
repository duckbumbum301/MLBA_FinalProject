"""
Test CRUD Customer Operations
Kiểm tra Create, Read, Update, Delete khách hàng
"""
from database.connector import DatabaseConnector
from config.database_config import DatabaseConfig
from services.query_service import QueryService
from models.customer import Customer

# Setup
config = DatabaseConfig()
db = DatabaseConnector(config)
db.connect()

query_service = QueryService(db)

print("="*70)
print("TEST CRUD OPERATIONS - KHÁCH HÀNG")
print("="*70)

# Test CREATE
print("\n1. CREATE - Tạo khách hàng mới")
print("-"*70)

test_customer = Customer(
    customer_name="Nguyễn Văn Test",
    customer_id_card="999999999999",  # CMND test
    LIMIT_BAL=100000,
    SEX=1,
    EDUCATION=2,
    MARRIAGE=1,
    AGE=35,
    PAY_0=-1, PAY_2=-1, PAY_3=0, PAY_4=-1, PAY_5=0, PAY_6=-1,
    PAY_7=0, PAY_8=-1, PAY_9=0, PAY_10=-1, PAY_11=0, PAY_12=-1,
    BILL_AMT1=10000, BILL_AMT2=9000, BILL_AMT3=11000, BILL_AMT4=8000,
    BILL_AMT5=10000, BILL_AMT6=9000, BILL_AMT7=10000, BILL_AMT8=8000,
    BILL_AMT9=9000, BILL_AMT10=10000, BILL_AMT11=8000, BILL_AMT12=9000,
    PAY_AMT1=10000, PAY_AMT2=9000, PAY_AMT3=11000, PAY_AMT4=8000,
    PAY_AMT5=10000, PAY_AMT6=9000, PAY_AMT7=10000, PAY_AMT8=8000,
    PAY_AMT9=9000, PAY_AMT10=10000, PAY_AMT11=8000, PAY_AMT12=9000
)

customer_id = query_service.save_customer(test_customer)
if customer_id:
    print(f"✓ Đã tạo customer ID: {customer_id}")
else:
    print("✗ Không thể tạo customer")

# Test READ
print("\n2. READ - Đọc thông tin khách hàng")
print("-"*70)

customer = query_service.get_customer_by_cmnd("999999999999")
if customer:
    print(f"✓ Tìm thấy: {customer.customer_name}")
    print(f"  - CMND: {customer.customer_id_card}")
    print(f"  - Hạn mức: {customer.LIMIT_BAL:,.0f} NT$ = {customer.LIMIT_BAL*800:,.0f} VND")
    print(f"  - Tuổi: {customer.AGE}")
    print(f"  - PAY_0: {customer.PAY_0}")
else:
    print("✗ Không tìm thấy customer")

# Test UPDATE
print("\n3. UPDATE - Cập nhật thông tin khách hàng")
print("-"*70)

if customer:
    customer.customer_name = "Nguyễn Văn Test - Updated"
    customer.LIMIT_BAL = 200000  # Tăng hạn mức
    customer.AGE = 36  # Tăng tuổi
    
    success = query_service.update_customer("999999999999", customer)
    if success:
        print("✓ Đã cập nhật thông tin")
        
        # Verify update
        updated = query_service.get_customer_by_cmnd("999999999999")
        if updated:
            print(f"  - Tên mới: {updated.customer_name}")
            print(f"  - Hạn mức mới: {updated.LIMIT_BAL:,.0f} NT$")
            print(f"  - Tuổi mới: {updated.AGE}")
    else:
        print("✗ Không thể cập nhật")

# Test DELETE
print("\n4. DELETE - Xóa khách hàng")
print("-"*70)

success = query_service.delete_customer("999999999999")
if success:
    print("✓ Đã xóa customer")
    
    # Verify delete
    deleted = query_service.get_customer_by_cmnd("999999999999")
    if not deleted:
        print("✓ Xác nhận: Customer đã bị xóa khỏi database")
    else:
        print("✗ Lỗi: Customer vẫn còn trong database")
else:
    print("✗ Không thể xóa customer")

db.close()

print()
print("="*70)
print("✓ HOÀN THÀNH TEST CRUD")
print("="*70)
print()
print("Các tính năng CRUD đã sẵn sàng trong UI:")
print("  - 💾 Lưu Khách Hàng (Create/Update)")
print("  - 🔍 Tìm Kiếm (Read)")
print("  - 🗑️ Xóa Khách Hàng (Delete)")
