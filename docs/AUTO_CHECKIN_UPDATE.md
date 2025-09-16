# 🔄 Auto Check-in Update System

## 🎯 **Tính năng**
Hệ thống tự động cập nhật check-in khi có thay đổi về khu vực (tạo mới, cập nhật bán kính, xóa).

## ✅ **Các thành phần đã thêm**

### **1. Django Signals**
- **`post_save`**: Tự động cập nhật check-in khi area được tạo/cập nhật
- **`post_delete`**: Xử lý check-in khi area bị xóa
- **Tự động chạy** khi có thay đổi về area

### **2. Management Commands**
- **`update_checkin_areas.py`**: Cập nhật check-in cũ chưa có area
- **`update_all_checkins_areas.py`**: Cập nhật tất cả check-in dựa trên area hiện có

### **3. API Endpoint**
- **`/checkin/update-checkins-areas/`**: API để admin trigger cập nhật check-in
- **Chỉ admin/manager** mới có quyền sử dụng

### **4. UI Button**
- **Nút "Cập nhật Check-in"** trong trang quản lý khu vực
- **Xác nhận trước khi cập nhật** để tránh lỗi
- **Hiển thị kết quả** cập nhật

## 🧪 **Cách sử dụng**

### **1. Tự động cập nhật (Signals)**
- **Tạo area mới**: Check-in tự động được cập nhật
- **Cập nhật bán kính**: Check-in trong vùng mới được cập nhật
- **Xóa area**: Check-in được chuyển về area khác hoặc location

### **2. Cập nhật thủ công (UI)**
1. Mở trang **Quản lý khu vực**
2. Click nút **"Cập nhật Check-in"**
3. **Xác nhận** trong popup
4. **Chờ kết quả** cập nhật

### **3. Cập nhật thủ công (Command)**
```bash
# Cập nhật check-in chưa có area
python3 manage.py update_checkin_areas

# Cập nhật tất cả check-in (bao gồm cả đã có area)
python3 manage.py update_all_checkins_areas --force

# Dry run (chỉ xem kết quả, không cập nhật)
python3 manage.py update_all_checkins_areas --dry-run
```

## 🔧 **Technical Details**

### **1. Django Signals**
```python
@receiver(post_save, sender=Area)
def update_checkins_on_area_change(sender, instance, created, **kwargs):
    # Tìm check-in phù hợp với area mới/cập nhật
    # Cập nhật area và distance_m
    # Ưu tiên area gần nhất
```

### **2. Management Command**
```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Lấy tất cả check-in
        # So sánh với tất cả area
        # Chọn area/location phù hợp nhất
        # Cập nhật database
```

### **3. API Endpoint**
```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_checkins_areas_api(request):
    # Kiểm tra quyền admin/manager
    # Chạy management command
    # Trả về kết quả
```

## 📱 **Expected Results**

### **Before Auto Update**
- ❌ Check-in cũ không được cập nhật khi có area mới
- ❌ Phải cập nhật thủ công
- ❌ Dữ liệu không nhất quán

### **After Auto Update**
- ✅ **Tự động cập nhật** khi có thay đổi area
- ✅ **Cập nhật thủ công** qua UI hoặc command
- ✅ **Dữ liệu nhất quán** giữa area và check-in
- ✅ **Trải nghiệm admin** tốt hơn

## 🚀 **Test Commands**

### **1. Test Signals**
```python
# Tạo area mới
area = Area.objects.create(
    name="Test Area",
    lat=20.9970,
    lng=105.8028,
    radius_m=100
)

# Kiểm tra check-in được cập nhật
checkins = Checkin.objects.filter(area=area)
print(f"Check-ins in new area: {checkins.count()}")
```

### **2. Test Management Command**
```bash
# Dry run
python3 manage.py update_all_checkins_areas --dry-run

# Actual update
python3 manage.py update_all_checkins_areas
```

### **3. Test API**
```bash
curl -X POST http://localhost:3000/checkin/update-checkins-areas/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN"
```

## 📊 **File Changes**

### **checkin/signals.py** (NEW)
- ✅ Django signals for auto-update
- ✅ post_save signal for area changes
- ✅ post_delete signal for area deletion

### **checkin/apps.py**
- ✅ Registered signals in ready() method

### **checkin/management/commands/update_all_checkins_areas.py** (NEW)
- ✅ Management command for updating all check-ins
- ✅ Support for dry-run and force modes
- ✅ Detailed logging and output

### **checkin/views.py**
- ✅ Added update_checkins_areas_api endpoint
- ✅ Admin/manager permission check
- ✅ Command execution with output capture

### **checkin/urls.py**
- ✅ Added URL for update-checkins-areas API
- ✅ Imported new view function

### **templates/checkin/area_management_new.html**
- ✅ Added "Cập nhật Check-in" button
- ✅ JavaScript for API call
- ✅ Loading state and error handling

## 🎯 **Benefits**

### **Automatic Updates**
- ✅ **Real-time sync** between areas and check-ins
- ✅ **No manual intervention** required
- ✅ **Consistent data** across the system

### **Manual Control**
- ✅ **Admin can trigger** updates when needed
- ✅ **Dry run mode** for testing
- ✅ **Detailed logging** for debugging

### **User Experience**
- ✅ **Seamless updates** without data loss
- ✅ **Intuitive UI** for manual updates
- ✅ **Clear feedback** on update results

---

**Implementation Date:** 16/09/2025  
**Status:** ✅ COMPLETED  
**Features:** Auto-update + Manual update + API + UI
