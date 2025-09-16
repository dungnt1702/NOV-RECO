# Hướng dẫn cấu hình Google Maps API

## 🗺️ Cấu hình Google Maps cho hệ thống check-in

### Bước 1: Tạo Google Cloud Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Đăng nhập bằng tài khoản Google
3. Tạo project mới hoặc chọn project hiện có

### Bước 2: Bật Google Maps JavaScript API
1. Vào **APIs & Services** > **Library**
2. Tìm kiếm "Maps JavaScript API"
3. Nhấn **Enable**

### Bước 3: Tạo API Key
1. Vào **APIs & Services** > **Credentials**
2. Nhấn **+ CREATE CREDENTIALS** > **API Key**
3. Copy API key được tạo

### Bước 4: Cấu hình API Key
1. Mở file `templates/checkin/checkin.html`
2. Tìm dòng:
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places&callback=initMap" async defer></script>
   ```
3. Thay thế `YOUR_API_KEY` bằng API key thực tế

### Bước 5: Cấu hình bảo mật (Tùy chọn)
1. Vào **APIs & Services** > **Credentials**
2. Nhấn vào API key vừa tạo
3. Cấu hình **Application restrictions**:
   - **HTTP referrers**: Thêm `http://localhost:3000/*`, `https://yourdomain.com/*`
4. Cấu hình **API restrictions**:
   - Chọn "Restrict key" và chỉ chọn "Maps JavaScript API"

### Bước 6: Test
1. Khởi động server: `./quick_start.sh`
2. Truy cập: http://localhost:3000/checkin/
3. Kiểm tra xem Google Maps có hiển thị không

## ⚠️ Lưu ý quan trọng

### Giới hạn sử dụng
- Google Maps API có giới hạn miễn phí hàng tháng
- Vượt quá giới hạn sẽ bị tính phí
- Theo dõi usage trong Google Cloud Console

### Bảo mật
- **KHÔNG** commit API key vào Git
- Sử dụng biến môi trường cho production
- Cấu hình restrictions để tránh lạm dụng

### Fallback
- Nếu không có API key, hệ thống vẫn hoạt động
- Chỉ hiển thị thông báo "API chưa được cấu hình"
- Chức năng lấy GPS vẫn hoạt động bình thường

## 🔧 Cấu hình nâng cao

### Sử dụng biến môi trường
```python
# settings.py
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY')
```

### Template động
```html
<script src="https://maps.googleapis.com/maps/api/js?key={{ GOOGLE_MAPS_API_KEY }}&libraries=places&callback=initMap" async defer></script>
```

## 📞 Hỗ trợ
Nếu gặp vấn đề, kiểm tra:
1. API key có đúng không
2. Maps JavaScript API đã được enable chưa
3. Restrictions có chặn domain không
4. Console có lỗi gì không
