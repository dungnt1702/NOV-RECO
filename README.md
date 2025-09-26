# 🏢 NOV-RECO Check-in Management System

Hệ thống quản lý check-in hiện đại với Django, Bootstrap và Leaflet.js.

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd checkin_project

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 3000
```

## 📚 Documentation

Tất cả tài liệu được tổ chức trong thư mục [`docs/`](./docs/):

- **[📖 User Guide](./docs/user-guides/USER_GUIDE.md)** - Hướng dẫn sử dụng
- **[⚡ Quick Reference](./docs/user-guides/QUICK-REFERENCE.md)** - Tham khảo nhanh
- **[🔧 Installation](./docs/development/INSTALLATION.md)** - Hướng dẫn cài đặt
- **[🚀 Deployment](./docs/deployment/DEPLOYMENT.md)** - Hướng dẫn triển khai
- **[🔐 Permissions](./docs/permissions/PERMISSION_SYSTEM_COMPLETION.md)** - Hệ thống phân quyền

## ✨ Features

### 🔐 Permission System
- **Django Groups + Permissions** - Hệ thống phân quyền linh hoạt
- **6 User Roles** - Super Admin, Admin, Manager, HR, Secretary, Employee
- **Granular Permissions** - 29 custom permissions

### 📍 Check-in Management
- **GPS-based Check-in** - Sử dụng vị trí thực tế
- **Photo Capture** - Chụp ảnh khi check-in
- **Area Detection** - Tự động phát hiện khu vực
- **Real-time Validation** - Kiểm tra quyền truy cập

### 🗺️ Area Management
- **Interactive Maps** - Sử dụng Leaflet.js
- **Radius-based Areas** - Địa điểm theo bán kính
- **Drag & Drop** - Kéo thả để tạo khu vực
- **Real-time Preview** - Xem trước khu vực

### 👥 User Management
- **Department Management** - Quản lý phòng ban
- **Role Assignment** - Phân quyền người dùng
- **Profile Management** - Quản lý thông tin cá nhân
- **Bulk Operations** - Thao tác hàng loạt

### 📊 Reporting & Analytics
- **Check-in History** - Lịch sử check-in
- **Department Reports** - Báo cáo phòng ban
- **Area Statistics** - Thống kê khu vực
- **Export Data** - Xuất dữ liệu

### 🤖 Automation Testing
- **Test Dashboard** - Giao diện quản lý tests
- **Real-time Execution** - Chạy tests thời gian thực
- **Progress Tracking** - Theo dõi tiến độ
- **Results Management** - Quản lý kết quả

## 🛠️ Technology Stack

- **Backend**: Django 5.0, Django REST Framework
- **Frontend**: Bootstrap 5, Leaflet.js, JavaScript ES6
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Authentication**: Django Allauth
- **Maps**: Leaflet.js với OpenStreetMap
- **Icons**: FontAwesome
- **Testing**: Django Test Framework

## 📱 Responsive Design

- **Mobile-first** - Tối ưu cho mobile
- **Progressive Web App** - Có thể cài đặt như app
- **Offline Support** - Hoạt động offline cơ bản
- **Touch-friendly** - Thân thiện với cảm ứng

## 🔒 Security Features

- **HTTPS Only** - Bảo mật kết nối
- **Permission-based Access** - Kiểm soát quyền truy cập
- **CSRF Protection** - Bảo vệ CSRF
- **XSS Prevention** - Ngăn chặn XSS
- **SQL Injection Protection** - Bảo vệ SQL injection

## 📈 Performance

- **Database Optimization** - Tối ưu database queries
- **Static Files Caching** - Cache static files
- **Image Optimization** - Tối ưu hình ảnh
- **Lazy Loading** - Tải lazy cho performance

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@nov-reco.com

---

**Made with ❤️ by NOV-RECO Team**
