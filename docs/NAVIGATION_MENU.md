# 📱 Navigation Menu - Hướng dẫn sử dụng

## Tổng quan

Hệ thống đã được bổ sung navigation menu responsive với khả năng toggle trên màn hình điện thoại, cung cấp trải nghiệm người dùng tốt hơn trên tất cả các thiết bị.

## ✨ Tính năng chính

### 🖥️ **Desktop Navigation**
- Menu ngang với logo và các liên kết
- Hiển thị thông tin người dùng và nút đăng xuất
- Hover effects và animations mượt mà

### 📱 **Mobile Navigation**
- **Hamburger menu** (☰) để toggle menu từ bên phải
- Menu slide-in từ bên phải, chỉ chiếm nửa màn hình
- Overlay tối để đóng menu
- **Auto-close** khi click ra ngoài menu
- Responsive design cho tất cả kích thước màn hình

### 🎯 **Menu Items**
- **Trang chủ**: Dashboard chính
- **Check-in**: Trang check-in chính
- **Lịch sử**: Lịch sử check-in của user
- **Danh sách Check-in**: Xem tất cả check-in (Manager/Admin)
- **Quản lý Khu vực**: Quản lý areas (Manager/Admin)
- **Quản lý User**: Quản lý người dùng (Admin only)

## 🛠️ **Cách sử dụng**

### **Desktop**
1. Menu luôn hiển thị ở đầu trang
2. Click vào các menu item để điều hướng
3. Hover để xem hiệu ứng

### **Mobile**
1. Click vào icon ☰ (hamburger) ở góc phải
2. Menu sẽ slide-in từ bên phải (chiếm nửa màn hình)
3. Click vào menu item để điều hướng
4. Click ra ngoài menu, vào overlay tối, hoặc icon ✕ để đóng menu

### **Keyboard Shortcuts**
- **Escape**: Đóng menu mobile
- **Tab**: Điều hướng qua các menu items

## 🎨 **Thiết kế**

### **Colors**
- **Primary**: #0A5597 (NOV-RECO Blue)
- **Secondary**: #F5831F (NOV-RECO Orange)
- **Background**: White với backdrop blur
- **Text**: #333 (Dark gray)

### **Typography**
- **Font**: -apple-system, BlinkMacSystemFont, 'Segoe UI'
- **Logo**: 1.2rem, font-weight: 700
- **Menu items**: 1rem, font-weight: 500

### **Animations**
- **Slide-in**: 0.3s ease
- **Hover**: translateY(-2px)
- **Fade**: 0.3s ease

## 📱 **Responsive Breakpoints**

### **Desktop (> 768px)**
- Menu ngang với tất cả items
- User info hiển thị đầy đủ
- Logo và text đầy đủ

### **Tablet (≤ 768px)**
- Hamburger menu xuất hiện
- Menu slide-in từ phải (50% màn hình)
- User info compact

### **Mobile (≤ 480px)**
- Logo nhỏ hơn
- Menu slide-in từ phải (60% màn hình)
- Menu items nhỏ hơn
- User name ẩn, chỉ hiển thị avatar

## 🔧 **Technical Implementation**

### **Base Template**
```html
<!-- templates/base.html -->
<nav class="navbar">
  <div class="nav-container">
    <a href="/" class="nav-logo">
      <img src="/static/logo.svg" alt="NOV-RECO Logo">
      <span>NOV-RECO</span>
    </a>
    
    <ul class="nav-menu" id="navMenu">
      <!-- Menu items -->
    </ul>
    
    <div class="user-info">
      <!-- User info -->
    </div>
    
    <button class="nav-toggle" id="navToggle">
      <i class="fas fa-bars"></i>
    </button>
  </div>
</nav>
```

### **CSS Classes**
- `.navbar`: Container chính
- `.nav-container`: Flex container
- `.nav-menu`: Menu items
- `.nav-toggle`: Hamburger button
- `.nav-overlay`: Mobile overlay

### **JavaScript Functions**
- `toggleNav()`: Toggle mobile menu
- `closeNav()`: Đóng mobile menu
- Event listeners cho click, escape, resize
- **Auto-close**: Tự động đóng khi click ra ngoài menu

## 🚀 **Cách tích hợp**

### **1. Sử dụng Base Template**
```html
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
<!-- Page content -->
{% endblock %}
```

### **2. Custom CSS**
```html
{% block extra_css %}
<style>
  /* Custom styles */
</style>
{% endblock %}
```

### **3. Custom JavaScript**
```html
{% block extra_js %}
<script>
  // Custom JavaScript
</script>
{% endblock %}
```

## 📋 **Menu Items theo Role**

### **Guest (Chưa đăng nhập)**
- Trang chủ
- Đăng nhập

### **Employee**
- Trang chủ
- Check-in
- Lịch sử
- Đăng xuất

### **Manager**
- Trang chủ
- Check-in
- Lịch sử
- Danh sách Check-in
- Quản lý Khu vực
- Đăng xuất

### **Admin**
- Trang chủ
- Check-in
- Lịch sử
- Danh sách Check-in
- Quản lý Khu vực
- Quản lý User
- Đăng xuất

## 🎯 **Active State**

Menu item sẽ được highlight khi:
- URL hiện tại khớp với menu item
- Sử dụng `request.resolver_match.url_name`

```html
<li><a href="/checkin/" class="{% if request.resolver_match.url_name == 'checkin_page' %}active{% endif %}">
  <i class="fas fa-map-marker-alt"></i> Check-in
</a></li>
```

## 🔍 **Troubleshooting**

### **Menu không hiển thị**
- Kiểm tra CSS đã load
- Kiểm tra JavaScript console
- Kiểm tra Font Awesome icons

### **Mobile menu không hoạt động**
- Kiểm tra JavaScript event listeners
- Kiểm tra CSS media queries
- Kiểm tra z-index

### **Menu items không đúng**
- Kiểm tra user permissions
- Kiểm tra URL patterns
- Kiểm tra template context

## 🚀 **Tương lai**

- [ ] Search functionality trong menu
- [ ] Notifications badge
- [ ] Dark mode toggle
- [ ] Menu customization
- [ ] Breadcrumb navigation
- [ ] Quick actions menu

---

**Cập nhật lần cuối:** 16/09/2025  
**Phiên bản:** 1.0.0
