# Quản lý Khu vực Check-in

## Tổng quan

Tính năng quản lý khu vực cho phép Admin và Manager định nghĩa các khu vực check-in trên bản đồ. Khi nhân viên check-in trong khu vực đã định nghĩa, hệ thống sẽ tự động nhận diện và gán tên khu vực cho check-in đó.

## Tính năng chính

### 1. Tạo Khu vực Mới
- **Tên khu vực**: Tên hiển thị cho khu vực
- **Mô tả**: Mô tả chi tiết về khu vực (tùy chọn)
- **Vị trí trung tâm**: Tọa độ lat/lng của tâm khu vực
- **Bán kính**: Khoảng cách từ tâm (tính bằng mét)
- **Bản đồ tương tác**: Click trên bản đồ để chọn vị trí

### 2. Quản lý Khu vực
- Xem danh sách tất cả khu vực
- Sửa thông tin khu vực
- Xóa khu vực
- Bật/tắt khu vực

### 3. Logic Check-in
- Hệ thống ưu tiên tìm khu vực (Area) trước
- Nếu không tìm thấy khu vực, fallback về Location cũ
- Tự động gán tên khu vực cho check-in

## Cách sử dụng

### Truy cập trang quản lý
1. Đăng nhập với tài khoản Admin hoặc Manager
2. Truy cập: `http://localhost:3000/checkin/area-management/`

### Tạo khu vực mới
1. Điền thông tin cơ bản (tên, mô tả)
2. Click trên bản đồ để chọn vị trí trung tâm
3. Điều chỉnh bán kính (10m - 10km)
4. Click "Tạo Khu vực"

### Quản lý khu vực
- **Xem danh sách**: Tất cả khu vực hiển thị trong danh sách
- **Sửa**: Click nút "Sửa" (tính năng đang phát triển)
- **Xóa**: Click nút "Xóa" và xác nhận

## API Endpoints

### Lấy danh sách khu vực
```
GET /checkin/areas/
```

### Tạo khu vực mới
```
POST /checkin/areas/
Content-Type: application/json

{
    "name": "Tên khu vực",
    "description": "Mô tả",
    "lat": 20.9970,
    "lng": 105.8028,
    "radius_m": 100
}
```

### Lấy chi tiết khu vực
```
GET /checkin/areas/{id}/
```

### Cập nhật khu vực
```
PUT /checkin/areas/{id}/
Content-Type: application/json

{
    "name": "Tên mới",
    "is_active": true
}
```

### Xóa khu vực
```
DELETE /checkin/areas/{id}/
```

## Cấu trúc Database

### Model Area
```python
class Area(models.Model):
    name = models.CharField(max_length=120)  # Tên khu vực
    description = models.TextField(blank=True)  # Mô tả
    lat = models.FloatField()  # Vĩ độ trung tâm
    lng = models.FloatField()  # Kinh độ trung tâm
    radius_m = models.PositiveIntegerField(default=100)  # Bán kính
    is_active = models.BooleanField(default=True)  # Trạng thái
    created_by = models.ForeignKey(User)  # Người tạo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Model Checkin (cập nhật)
```python
class Checkin(models.Model):
    user = models.ForeignKey(User)
    area = models.ForeignKey(Area, null=True, blank=True)  # Khu vực mới
    location = models.ForeignKey(Location, null=True, blank=True)  # Location cũ
    # ... các trường khác
```

## Quyền truy cập

- **Admin**: Toàn quyền quản lý khu vực
- **Manager**: Toàn quyền quản lý khu vực
- **Employee**: Chỉ xem được khu vực trong check-in

## Lưu ý kỹ thuật

1. **Ưu tiên Area**: Hệ thống tìm Area trước, sau đó mới tìm Location
2. **Bán kính**: Sử dụng công thức Haversine để tính khoảng cách
3. **Performance**: Sử dụng `select_related` để tối ưu query
4. **Validation**: Kiểm tra tọa độ hợp lệ và bán kính trong phạm vi cho phép

## Troubleshooting

### Lỗi thường gặp
1. **"Permission denied"**: Kiểm tra quyền Admin/Manager
2. **"Khu vực không tồn tại"**: ID khu vực không hợp lệ
3. **"Tọa độ không hợp lệ"**: Kiểm tra giá trị lat/lng

### Debug
- Kiểm tra logs trong terminal Django
- Sử dụng Django Admin để xem dữ liệu
- Kiểm tra network tab trong DevTools

## Tương lai

- [ ] Tính năng sửa khu vực trên giao diện web
- [ ] Import/Export khu vực từ file CSV
- [ ] Thống kê check-in theo khu vực
- [ ] Bản đồ hiển thị tất cả khu vực
- [ ] Thông báo khi nhân viên check-in ngoài khu vực
