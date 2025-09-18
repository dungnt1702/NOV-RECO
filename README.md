# NOV-RECO Check-in System

Hệ thống check-in thông minh với phân quyền người dùng và quản lý địa điểm.

## 🚀 Quick Start

### **Cài đặt tự động (Khuyến nghị)**
```bash
# Clone repository
git clone https://github.com/dungnt1702/NOV-RECO.git
cd NOV-RECO

# Chạy setup hoàn chỉnh
data\scripts\setup_complete_data.bat

# Khởi động server
data\scripts\start_reco_local.bat
```

### **Truy cập hệ thống**
- **🌐 Website**: http://reco.local (hoặc http://localhost:3000)
- **⚙️ Admin Panel**: http://reco.local/admin

### **Tài khoản mẫu**
| Vai trò | Username | Password | Quyền hạn |
|---------|----------|----------|-----------|
| 🔴 Super Admin | `superadmin` | `admin123` | Toàn quyền hệ thống |
| 🟡 Quản lý | `quanly` | `quanly123` | Xem và sửa toàn bộ |
| 🟢 Thư ký | `thuky` | `thuky123` | Xem và sửa (trừ user mgmt) |
| 🔵 Nhân viên | `nhanvien1` | `nhanvien123` | Xem và checkin |

## 📚 Tài liệu

Tất cả tài liệu chi tiết được tổ chức trong thư mục `docs/`:

| Tài liệu | Mô tả |
|----------|-------|
| 📋 [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Cấu trúc dự án và kiến trúc |
| 🛠️ [INSTALLATION.md](docs/INSTALLATION.md) | Hướng dẫn cài đặt chi tiết |
| 👥 [USER_MANAGEMENT.md](docs/USER_MANAGEMENT.md) | Hệ thống phân quyền người dùng |
| 📖 [INDEX.md](docs/INDEX.md) | Danh mục tài liệu đầy đủ |

## ✨ Tính năng chính

- 🔐 **Hệ thống phân quyền 4 cấp**: Super Admin, Quản lý, Thư ký, Nhân viên
- 📍 **Check-in GPS**: Xác thực vị trí với bán kính cho phép
- 📱 **Responsive Design**: Giao diện thân thiện trên mọi thiết bị
- 📊 **Dashboard theo vai trò**: Giao diện tùy chỉnh cho từng loại người dùng
- 👥 **Quản lý người dùng**: Tạo và phân quyền tài khoản
- 📸 **Camera**: Chụp ảnh check-in trực tiếp
- 🗺️ **Bản đồ**: OpenStreetMap tích hợp
- 📋 **Lịch sử**: Xem lịch sử check-in
- ⚡ **Check-in nhanh**: Sử dụng dữ liệu từ lần trước

## 🏗️ Cấu trúc dự án

```
checkin.reco.vn/
├── 📁 data/                       # 🆕 Dữ liệu và cấu hình
│   ├── 📁 scripts/                # Scripts tiện ích
│   │   ├── setup_complete_data.bat    # Setup toàn bộ dữ liệu
│   │   └── start_reco_local.bat       # Khởi động server
│   └── db.sqlite3                 # Database SQLite
├── 📁 checkin/                    # Django app chính
├── 📁 users/                      # Quản lý người dùng
├── 📁 templates/                  # HTML templates
├── 📁 static/                     # CSS, JS, images
├── 📁 docs/                       # 📚 Tài liệu dự án
└── manage.py                      # Django management
```

## 🔧 Cài đặt thủ công

### 1. Cài đặt Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Thiết lập database
```bash
python manage.py migrate
```

### 3. Tạo dữ liệu mẫu
```bash
python manage.py setup_user_groups
python manage.py create_sample_users
python manage.py create_sample_areas
```

### 4. Khởi động server
```bash
python manage.py runserver 3000
```

## 🌐 Cài đặt Virtual Host (reco.local)

### Windows + XAMPP
1. **Chỉnh sửa hosts file**:
   ```
   # C:\Windows\System32\drivers\etc\hosts
   127.0.0.1    reco.local
   ```

2. **Cấu hình Apache Virtual Host**:
   ```apache
   # C:\xampp\apache\conf\extra\httpd-vhosts.conf
   <VirtualHost *:80>
       ServerName reco.local
       ProxyPass / http://127.0.0.1:3000/
       ProxyPassReverse / http://127.0.0.1:3000/
   </VirtualHost>
   ```

3. **Restart Apache** và truy cập: http://reco.local

## 👥 Phân quyền người dùng

| Vai trò | User Mgmt | Area Mgmt | Checkin | Admin Panel |
|---------|-----------|-----------|---------|-------------|
| 🔴 Super Admin | ✅ Full | ✅ Full | ✅ Full | ✅ Yes |
| 🟡 Quản lý | ✅ Add/Edit/View | ✅ Full | ✅ Full | ✅ Limited |
| 🟢 Thư ký | ✅ View only | ✅ Add/Edit/View | ✅ Add/Edit/View | ✅ Limited |
| 🔵 Nhân viên | ❌ No | ✅ View only | ✅ Add/View own | ❌ No |

## 🏢 Dữ liệu mẫu

### Khu vực check-in
- 📍 Văn phòng Hà Nội (200m radius)
- 📍 Chi nhánh TP.HCM (150m radius)
- 📍 Nhà máy Bắc Ninh (300m radius)
- 📍 Kho hàng Đồng Nai (250m radius)
- 📍 Showroom Đà Nẵng (100m radius)

## 🔧 Troubleshooting

### Lỗi thường gặp

#### Python không tìm thấy
```bash
# Sử dụng đường dẫn đầy đủ
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
```

#### Port 3000 đã được sử dụng
```bash
python manage.py runserver 3001
```

#### Database locked
```bash
# Dừng Django server trước khi thao tác với database
```

### Kiểm tra hệ thống
```bash
python manage.py check
python manage.py showmigrations
```

## 📞 Hỗ trợ

- **📖 Tài liệu**: Xem thư mục `docs/`
- **🐛 Báo lỗi**: GitHub Issues
- **📧 Email**: developer@checkin.reco.vn

---

**Cập nhật lần cuối:** 19/09/2025  
**Phiên bản:** 2.0.0  
**Tác giả:** NOV-RECO Development Team