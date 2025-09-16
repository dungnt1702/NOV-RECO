# NOV-RECO Check-in System

Hệ thống check-in thông minh với phân quyền người dùng và quản lý địa điểm.

## 🚀 Quick Start

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy migrations
```bash
python manage.py migrate
```

### 3. Tạo admin
```bash
python manage.py create_admin
```

### 4. Khởi động server
```bash
python manage.py runserver 3000
```

### 5. Truy cập
- **URL**: http://localhost:3000
- **Admin**: admin@nov-reco.com / admin123

## 📚 Tài liệu

Tất cả tài liệu chi tiết được tổ chức trong thư mục [`docs/`](./docs/):

- **[INDEX.md](./docs/INDEX.md)** - Danh mục tài liệu đầy đủ
- **[README.md](./docs/README.md)** - Hướng dẫn cài đặt chi tiết
- **[GOOGLE_MAPS_SETUP.md](./docs/GOOGLE_MAPS_SETUP.md)** - Cài đặt Google Maps
- **[OPENSTREETMAP_SETUP.md](./docs/OPENSTREETMAP_SETUP.md)** - Cài đặt OpenStreetMap
- **[DEBUG_CHECKIN.md](./docs/DEBUG_CHECKIN.md)** - Debug check-in
- **[RESPONSIVE_TEST.md](./docs/RESPONSIVE_TEST.md)** - Test responsive
- **[SUCCESS_PAGE.md](./docs/SUCCESS_PAGE.md)** - Trang kết quả check-in
- **[SUCCESS_PAGE_UPDATE.md](./docs/SUCCESS_PAGE_UPDATE.md)** - Cập nhật trang kết quả

## ✨ Tính năng chính

- 🔐 **Hệ thống phân quyền**: Admin, Quản lý, Nhân viên
- 📍 **Check-in GPS**: Xác thực vị trí với bán kính cho phép
- 📱 **Responsive Design**: Giao diện thân thiện trên mọi thiết bị
- 📊 **Dashboard**: Thống kê và quản lý theo vai trò
- 👥 **Quản lý người dùng**: Tạo và phân quyền tài khoản
- 📸 **Camera**: Chụp ảnh check-in trực tiếp
- 🗺️ **Bản đồ**: OpenStreetMap tích hợp
- 📋 **Lịch sử**: Xem lịch sử check-in
- ⚡ **Check-in nhanh**: Sử dụng dữ liệu từ lần trước

## 🏗️ Cấu trúc dự án

```
checkin_project/
├── checkin/                 # Django app chính
├── templates/              # HTML templates
├── docs/                   # 📚 Tài liệu dự án
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
└── README.md             # File này
```

## 🔧 Troubleshooting

Nếu gặp lỗi, hãy tham khảo tài liệu trong thư mục [`docs/`](./docs/):

1. **Lỗi Google Maps:** Xem [GOOGLE_MAPS_SETUP.md](./docs/GOOGLE_MAPS_SETUP.md)
2. **Lỗi camera:** Xem [CAMERA_TEST.md](./docs/CAMERA_TEST.md)
3. **Lỗi responsive:** Xem [RESPONSIVE_TEST.md](./docs/RESPONSIVE_TEST.md)
4. **Lỗi check-in:** Xem [DEBUG_CHECKIN.md](./docs/DEBUG_CHECKIN.md)

---

**Cập nhật lần cuối:** 16/09/2024  
**Phiên bản:** 1.0.0
