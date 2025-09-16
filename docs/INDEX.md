# 📚 Tài liệu dự án Check-in NOV-RECO

## 🎯 **Tổng quan dự án**
Dự án hệ thống check-in cho công ty NOV-RECO với các tính năng:
- Check-in với vị trí GPS và camera
- Quản lý người dùng theo vai trò (Admin, Manager, Employee)
- Dashboard và báo cáo
- Lịch sử check-in và check-in nhanh

## 📋 **Danh sách tài liệu**

### 🚀 **Hướng dẫn cài đặt**
- [README.md](./README.md) - Hướng dẫn cài đặt và chạy dự án
- [GOOGLE_MAPS_SETUP.md](./GOOGLE_MAPS_SETUP.md) - Cài đặt Google Maps API
- [ENABLE_GOOGLE_MAPS.md](./ENABLE_GOOGLE_MAPS.md) - Kích hoạt Google Maps
- [OPENSTREETMAP_SETUP.md](./OPENSTREETMAP_SETUP.md) - Cài đặt OpenStreetMap (thay thế Google Maps)

### 🔧 **Hướng dẫn sửa lỗi**
- [DEBUG_CHECKIN.md](./DEBUG_CHECKIN.md) - Debug các lỗi check-in
- [ERROR_FIX.md](./ERROR_FIX.md) - Sửa lỗi AbortError và CSRF
- [FILE_EXTENSION_FIX.md](./FILE_EXTENSION_FIX.md) - Sửa lỗi file extension
- [CACHE_CLEAR.md](./CACHE_CLEAR.md) - Xóa cache browser

### 📱 **Responsive và UI**
- [RESPONSIVE_TEST.md](./RESPONSIVE_TEST.md) - Test responsive design
- [SPACING_FIX.md](./SPACING_FIX.md) - Sửa lỗi spacing
- [MAP_HEIGHT_FIX.md](./MAP_HEIGHT_FIX.md) - Sửa chiều cao map
- [CAMERA_PREVIEW_FIX.md](./CAMERA_PREVIEW_FIX.md) - Sửa lỗi camera preview
- [CAMERA_TEST.md](./CAMERA_TEST.md) - Test camera functionality

### ✨ **Tính năng mới**
- [FEATURE_UPDATE.md](./FEATURE_UPDATE.md) - Cập nhật tính năng check-in time và validation
- [AUTO_FEATURES.md](./AUTO_FEATURES.md) - Tính năng auto-location và auto-camera
- [SUCCESS_PAGE.md](./SUCCESS_PAGE.md) - Trang kết quả check-in
- [SUCCESS_PAGE_UPDATE.md](./SUCCESS_PAGE_UPDATE.md) - Cập nhật trang kết quả với lịch sử và check-in nhanh
- [AREA_MANAGEMENT.md](./AREA_MANAGEMENT.md) - Quản lý khu vực check-in cho Admin/Manager
- [NAVIGATION_MENU.md](./NAVIGATION_MENU.md) - Navigation menu responsive với mobile toggle

## 🏗️ **Cấu trúc dự án**

```
checkin_project/
├── checkin/                 # Django app chính
│   ├── models.py           # Models (User, Checkin, Location, Area)
│   ├── views.py            # Views và APIs
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # URL patterns
│   ├── admin.py            # Django admin
│   └── management/         # Management commands
├── templates/              # HTML templates
│   └── checkin/
│       ├── checkin.html    # Trang check-in chính
│       ├── checkin_success.html  # Trang kết quả
│       ├── user_history.html     # Lịch sử check-in
│       ├── quick_checkin.html    # Check-in nhanh
│       ├── area_management.html  # Quản lý khu vực
│       └── *.html          # Các trang khác
├── docs/                   # Tài liệu dự án
│   ├── INDEX.md           # File này
│   └── *.md              # Các tài liệu khác
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
└── README.md             # Hướng dẫn cài đặt
```

## 🚀 **Quick Start**

1. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Chạy migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Tạo superuser:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Chạy server:**
   ```bash
   python manage.py runserver 3000
   ```

5. **Truy cập:**
   - http://localhost:3000 - Trang chủ
   - http://localhost:3000/checkin/ - Check-in
   - http://localhost:3000/checkin/area-management/ - Quản lý khu vực (Admin/Manager)
   - http://localhost:3000/admin/ - Admin panel

## 🔧 **Troubleshooting**

Nếu gặp lỗi, hãy tham khảo các tài liệu trong thư mục `docs/`:

1. **Lỗi Google Maps:** Xem [GOOGLE_MAPS_SETUP.md](./GOOGLE_MAPS_SETUP.md)
2. **Lỗi camera:** Xem [CAMERA_TEST.md](./CAMERA_TEST.md)
3. **Lỗi responsive:** Xem [RESPONSIVE_TEST.md](./RESPONSIVE_TEST.md)
4. **Lỗi check-in:** Xem [DEBUG_CHECKIN.md](./DEBUG_CHECKIN.md)

## 📞 **Hỗ trợ**

Nếu cần hỗ trợ thêm, vui lòng tạo issue hoặc liên hệ team phát triển.

---

**Cập nhật lần cuối:** 16/09/2024
**Phiên bản:** 1.0.0
