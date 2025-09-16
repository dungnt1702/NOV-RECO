# 🗺️ Bật Google Maps API

## Cách nhanh để bật Google Maps:

### 1. Lấy API Key từ Google Cloud Console
1. Truy cập: https://console.cloud.google.com/
2. Tạo project mới hoặc chọn project hiện có
3. Vào **APIs & Services** > **Library**
4. Tìm "Maps JavaScript API" và bật
5. Vào **APIs & Services** > **Credentials**
6. Tạo **API Key** mới

### 2. Cập nhật template
Mở file `templates/checkin/checkin.html` và thay thế:

```html
<!-- Từ: -->
<!-- <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places&callback=initMap" async defer></script> -->

<!-- Thành: -->
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&libraries=places&callback=initMap" async defer></script>
```

### 3. Test
- Khởi động server: `./quick_start.sh`
- Truy cập: http://localhost:3000/checkin/
- Kiểm tra xem Google Maps có hiển thị không

## ⚠️ Lưu ý:
- Thay `YOUR_ACTUAL_API_KEY` bằng API key thực tế
- Cấu hình restrictions trong Google Cloud Console để bảo mật
- Hệ thống vẫn hoạt động bình thường ngay cả khi không có Google Maps
