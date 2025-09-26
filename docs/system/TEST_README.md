# NOV-RECO Check-in System - Test Module

Module test toàn diện cho hệ thống check-in NOV-RECO với dữ liệu mẫu đầy đủ và script test tự động.

## 📁 Cấu trúc Test Module

```
test_data_generator.py      # Tạo dữ liệu mẫu đầy đủ
test_system.py             # Test toàn bộ hệ thống
fix_common_issues.py       # Khắc phục lỗi phổ biến
run_comprehensive_test.py  # Chạy toàn bộ quá trình test
start_and_test.py          # Khởi động server và test
TEST_README.md             # Hướng dẫn sử dụng
```

## 🚀 Cách sử dụng

### 1. Chạy Test Toàn Diện (Khuyến nghị)

```bash
python run_comprehensive_test.py
```

Script này sẽ:
- ✅ Fix các lỗi phổ biến
- ✅ Tạo dữ liệu mẫu đầy đủ
- ✅ Collect static files
- ✅ Apply migrations
- ✅ Chạy test toàn bộ hệ thống

### 2. Chạy Test Riêng Lẻ

#### Tạo dữ liệu mẫu:
```bash
python test_data_generator.py
```

#### Test hệ thống:
```bash
python test_system.py
```

#### Fix lỗi phổ biến:
```bash
python fix_common_issues.py
```

#### Khởi động server và test:
```bash
python start_and_test.py
```

## 📊 Dữ liệu mẫu được tạo

### 👥 Người dùng (10+ users)
- **Admin**: admin / admin123
- **Manager**: manager1, manager2 / manager123
- **HCNS**: hcns1 / hcns123
- **Employee**: employee1-10 / employee123

### 🏢 Phòng ban (6 departments)
- Phòng Kỹ thuật
- Phòng Kinh doanh
- Phòng Nhân sự
- Phòng Kế toán
- Phòng Marketing
- Phòng Hành chính

### 📍 Địa điểm (5 areas)
- Văn phòng chính (19-21 Vũ Trọng Phụng)
- Chi nhánh Cầu Giấy
- Chi nhánh Đống Đa
- Kho hàng Long Biên
- Showroom Ba Đình

### 📸 Check-in (300+ records)
- 30 ngày dữ liệu
- 5-15 check-in mỗi ngày
- Ảnh mẫu tự động tạo
- Vị trí GPS ngẫu nhiên trong địa điểm

## 🧪 Các Test được thực hiện

### 1. Test Cơ bản
- ✅ Server đang chạy
- ✅ Trang chủ load được
- ✅ Static files load được
- ✅ URL patterns hoạt động

### 2. Test Authentication
- ✅ Trang đăng nhập
- ✅ Đăng nhập admin
- ✅ Đăng nhập employee
- ✅ Phân quyền đúng

### 3. Test Check-in Module
- ✅ Trang check-in action
- ✅ Trang lịch sử check-in
- ✅ Trang danh sách check-in
- ✅ API user info
- ✅ API check-in list

### 4. Test Area Management
- ✅ Trang danh sách địa điểm
- ✅ Trang tạo địa điểm
- ✅ API danh sách địa điểm

### 5. Test User Management
- ✅ Trang danh sách người dùng
- ✅ Trang tạo người dùng
- ✅ Trang quản lý phòng ban

### 6. Test Personal Profile
- ✅ Trang thông tin cá nhân
- ✅ Trang chỉnh sửa profile

### 7. Test Dashboard
- ✅ Dashboard admin

### 8. Test Database
- ✅ Số lượng users
- ✅ Số lượng areas
- ✅ Số lượng check-ins
- ✅ Phân quyền users

## 🔧 Các lỗi được tự động fix

### Database Issues
- ✅ Tạo migrations
- ✅ Apply migrations
- ✅ Kiểm tra integrity
- ✅ Sửa quyền database files

### Static Files
- ✅ Collect static files
- ✅ Tạo thư mục media
- ✅ Sửa quyền files

### Template Issues
- ✅ Kiểm tra syntax
- ✅ Kiểm tra URL references
- ✅ Kiểm tra static load

### Import Issues
- ✅ Kiểm tra import syntax
- ✅ Kiểm tra app references

### URL Issues
- ✅ Kiểm tra URL patterns
- ✅ Kiểm tra namespace

## 📈 Kết quả Test

Sau khi chạy test, bạn sẽ thấy:

```
============================================================
TEST SUMMARY
============================================================
Total Tests: 25
Passed: 23
Failed: 2
Success Rate: 92.0%

DETAILED RESULTS:
--------------------------------------------------
✅ PASS Step 1: Fix Common Issues
✅ PASS Step 2: Generate Test Data
✅ PASS Step 3: Collect Static Files
✅ PASS Step 4: Apply Database Migrations
❌ FAIL Step 5: Run System Tests
```

## 🎯 Mục tiêu

Module test này được thiết kế để:

1. **Tự động hóa** quá trình test
2. **Phát hiện lỗi** sớm và tự động
3. **Tạo dữ liệu mẫu** đầy đủ để test
4. **Khắc phục lỗi** phổ biến tự động
5. **Đảm bảo chất lượng** trước khi deploy

## ⚠️ Lưu ý

- Chạy test trong môi trường development
- Backup database trước khi chạy test
- Kiểm tra kết quả test trước khi deploy
- Sửa các lỗi còn lại thủ công nếu cần

## 🆘 Troubleshooting

### Lỗi "Port already in use"
```bash
# Tìm và kill process
lsof -ti:3000 | xargs kill -9
```

### Lỗi "Database is locked"
```bash
# Restart server
python manage.py runserver 127.0.0.1:3000
```

### Lỗi "Static files not found"
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Lỗi "Migration required"
```bash
# Tạo và apply migrations
python manage.py makemigrations
python manage.py migrate
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Log output của test
2. Django server logs
3. Browser console errors
4. Database integrity

---

**Tác giả**: NOV-RECO Development Team  
**Ngày tạo**: 2025-01-25  
**Phiên bản**: 1.0.0
