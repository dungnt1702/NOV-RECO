# Check-in Web App (Django + Google Sign-In)

Tính năng:
- Đăng nhập bằng Gmail (Google OAuth2/OpenID Connect) qua `django-allauth`.
- Trang web check-in: chọn địa điểm, lấy tọa độ GPS từ trình duyệt, upload ảnh, lưu DB.
- API bằng Django REST Framework.
- Lưu ảnh về `MEDIA/` (mặc định).

## 1) Cài đặt
```bash
cd checkin_project
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

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
