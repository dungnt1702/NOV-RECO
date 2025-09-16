# NOV-RECO Check-in System

Hệ thống check-in thông minh với phân quyền người dùng và quản lý địa điểm.

> 📚 **Tài liệu chi tiết:** Xem [INDEX.md](./INDEX.md) để biết danh sách đầy đủ các tài liệu hướng dẫn.

## ✨ Tính năng chính
- 🔐 **Hệ thống phân quyền**: Admin, Quản lý, Nhân viên
- 📍 **Check-in GPS**: Xác thực vị trí với bán kính cho phép
- 📱 **Responsive Design**: Giao diện thân thiện trên mọi thiết bị
- 📊 **Dashboard**: Thống kê và quản lý theo vai trò
- 👥 **Quản lý người dùng**: Tạo và phân quyền tài khoản
- 📸 **Upload ảnh**: Chụp ảnh check-in với xác thực
- 🌐 **Google OAuth**: Đăng nhập nhanh với Google

## 🚀 Khởi động nhanh

### Cách 1: Tự động khởi động (Khuyến nghị)
```bash
# Mở terminal trong thư mục dự án và chạy:
./quick_start.sh
```

### Cách 2: Khởi động thủ công
```bash
# Cài đặt dependencies
pip3 install -r requirements.txt

# Chạy migrations
python3 manage.py migrate

# Tạo admin (nếu chưa có)
python3 manage.py create_admin

# Khởi động server
python3 manage.py runserver 127.0.0.1:3000
```

### Cách 3: VS Code Auto Start
1. Mở dự án trong VS Code
2. Nhấn `Cmd+Shift+P` → "Tasks: Run Task" → "Start Django Server"
3. Hoặc mở file `start_server.py` và nhấn F5

## 🔑 Tài khoản mặc định
- **Admin**: admin@nov-reco.com / admin123
- **URL**: http://localhost:3000

## 2) Chạy server với port tùy chỉnh

### Cách 1: Sử dụng lệnh Django trực tiếp
```bash
# Chạy trên port 3000 (hoặc port bất kỳ)
python manage.py runserver 0.0.0.0:3000

# Chạy trên port 5000
python manage.py runserver 0.0.0.0:5000
```

### Cách 2: Sử dụng script Python
```bash
# Chạy với port mặc định (3000)
python run_server.py

# Chạy với port tùy chỉnh
python run_server.py 5000
```

### Cách 3: Sử dụng script Shell (Linux/Mac)
```bash
# Cấp quyền thực thi
chmod +x start_server.sh

# Chạy với port mặc định (3000)
./start_server.sh

# Chạy với port tùy chỉnh
./start_server.sh 5000
```

### Cách 4: Sử dụng biến môi trường
```bash
# Thiết lập port qua biến môi trường
export SERVER_PORT=3000
python run_server.py
```

Sau khi chạy, truy cập: http://localhost:[PORT] (thay [PORT] bằng port bạn đã chọn)

## 3) Cấu hình Google OAuth
- Truy cập Google Cloud Console → APIs & Services → OAuth consent screen (External).
- Tạo OAuth Client (Web application):
  - Authorized redirect URIs:
    - http://127.0.0.1:3000/accounts/google/login/callback/
    - http://localhost:3000/accounts/google/login/callback/
    - http://127.0.0.1:5000/accounts/google/login/callback/
    - http://localhost:5000/accounts/google/login/callback/
    - (Thêm các port khác nếu bạn sử dụng)
- Vào `/admin` → Social accounts → Social applications → Thêm Google app:
  - Client ID / Client Secret (từ Google)
  - Chọn Site = example.com (SITE_ID=1).

> Production: thêm `https://yourdomain.com/accounts/google/login/callback/` vào Authorized redirect URIs và dùng HTTPS.

## 4) Tạo địa điểm mẫu
Vào `/admin` → Checkin → Locations → Add:
- Name: "Điểm Check-in A"
- lat/lng: toạ độ vị trí
- radius_m: bán kính cho phép (ví dụ 150m)

## 5) Quy trình người dùng
1. Mở trang chủ → "Đăng nhập bằng Google".
2. Vào `/checkin/`.
3. Chọn địa điểm → bật GPS → chụp/tải ảnh → Gửi check-in.

## 6) Tuỳ chỉnh
- Chuyển sang PostgreSQL: sửa `DATABASES` trong `project/settings.py`.
- Giới hạn domain email nội bộ: thêm `HOSTED_DOMAIN` trong `SOCIALACCOUNT_PROVIDERS['google']`.
- Lưu ảnh lên S3/Cloud Storage: thay `DEFAULT_FILE_STORAGE` (không cấu hình sẵn trong mẫu).
