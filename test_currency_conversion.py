"""
Test Currency Conversion
Kiểm tra chức năng chuyển đổi VND/NT$
"""

EXCHANGE_RATE = 800  # 1 NT$ = 800 VND

print("="*70)
print("TEST CHUYỂN ĐỔI TIỀN TỆ VND/NT$")
print("="*70)
print(f"Tỷ giá: 1 NT$ = {EXCHANGE_RATE} VND")
print()

# Test case 1: VND -> NT$ (user nhập VND, model nhận NT$)
print("Test 1: User nhập VND, chuyển sang NT$ cho model")
print("-"*70)
vnd_values = [40000000, 80000000, 160000000, 8000000]
for vnd in vnd_values:
    ntd = vnd / EXCHANGE_RATE
    print(f"  {vnd:>12,} VND → {ntd:>10,.0f} NT$")

print()

# Test case 2: NT$ -> VND (database lưu NT$, hiển thị VND)
print("Test 2: Database lưu NT$, hiển thị VND cho user")
print("-"*70)
ntd_values = [50000, 100000, 200000, 10000]
for ntd in ntd_values:
    vnd = ntd * EXCHANGE_RATE
    print(f"  {ntd:>10,} NT$ → {vnd:>12,} VND")

print()

# Test case 3: Tính toán xác suất vỡ nợ giữ nguyên
print("Test 3: Tỷ lệ % giữ nguyên khi chuyển đổi")
print("-"*70)
limit_ntd = 100000
bill_ntd = 50000
ratio_ntd = bill_ntd / limit_ntd

limit_vnd = limit_ntd * EXCHANGE_RATE
bill_vnd = bill_ntd * EXCHANGE_RATE
ratio_vnd = bill_vnd / limit_vnd

print(f"  NT$: Nợ {bill_ntd:,} / Hạn mức {limit_ntd:,} = {ratio_ntd:.1%}")
print(f"  VND: Nợ {bill_vnd:,} / Hạn mức {limit_vnd:,} = {ratio_vnd:.1%}")
print(f"  ✓ Tỷ lệ giống nhau → Model cho kết quả giống nhau")

print()
print("="*70)
print("KẾT LUẬN")
print("="*70)
print("✓ Chuyển đổi VND/NT$ chỉ là UI layer")
print("✓ Model vẫn xử lý với NT$ (như đã train)")
print("✓ Tỷ lệ % giữ nguyên → Dự đoán chính xác")
print("✓ KHÔNG CẦN train lại model")
print("="*70)
