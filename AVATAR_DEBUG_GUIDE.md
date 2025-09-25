# Avatar Upload Debug Guide

## 🔍 Vấn đề hiện tại
Khi chọn ảnh để tải lên avatar, không có gì xảy ra sau khi chọn file.

## 🧪 Cách debug

### 1. Truy cập test page
```
http://localhost:3000/personal/avatar-test/
```

### 2. Mở Developer Tools
- **Chrome/Edge**: F12 hoặc Ctrl+Shift+I
- **Firefox**: F12 hoặc Ctrl+Shift+I
- **Safari**: Cmd+Option+I

### 3. Kiểm tra Console
Mở tab **Console** và thực hiện các bước sau:

#### Bước 1: Chọn file ảnh
- Click "Choose Image" và chọn một file ảnh
- Xem console có hiển thị:
  ```
  File selected: File {name: "image.jpg", size: 12345, type: "image/jpeg"}
  ```

#### Bước 2: Click Upload
- Click nút "Upload"
- Xem console có hiển thị:
  ```
  Response status: 200
  Response data: {success: true, message: "Cập nhật avatar thành công!", avatar_url: "/media/avatars/..."}
  ```

### 4. Kiểm tra Network tab
- Mở tab **Network**
- Chọn file và click Upload
- Xem có request POST đến `/personal/avatar-upload/` không
- Kiểm tra response status và data

## 🐛 Các lỗi có thể gặp

### Lỗi 1: File không được chọn
**Triệu chứng**: Không có log "File selected" trong console
**Nguyên nhân**: File input không hoạt động
**Giải pháp**: Kiểm tra HTML và JavaScript

### Lỗi 2: File validation failed
**Triệu chứng**: Log "Invalid file type" hoặc "File too large"
**Nguyên nhân**: File không phải ảnh hoặc quá lớn (>5MB)
**Giải pháp**: Chọn file ảnh nhỏ hơn 5MB

### Lỗi 3: Network request failed
**Triệu chứng**: Error trong console hoặc status code khác 200
**Nguyên nhân**: Server error hoặc CSRF token
**Giải pháp**: Kiểm tra server logs và CSRF token

### Lỗi 4: Response parsing failed
**Triệu chứng**: Error khi parse JSON response
**Nguyên nhân**: Server trả về HTML thay vì JSON
**Giải pháp**: Kiểm tra server view và error handling

## 🔧 Debug steps

### Step 1: Kiểm tra file selection
```javascript
// Trong console, chạy:
document.getElementById('avatar-input').addEventListener('change', function(e) {
    console.log('File selected:', e.target.files[0]);
});
```

### Step 2: Kiểm tra form submission
```javascript
// Trong console, chạy:
document.getElementById('test-upload-form').addEventListener('submit', function(e) {
    console.log('Form submitted');
    e.preventDefault();
});
```

### Step 3: Kiểm tra CSRF token
```javascript
// Trong console, chạy:
console.log('CSRF token:', document.querySelector('[name=csrfmiddlewaretoken]').value);
```

### Step 4: Test manual upload
```javascript
// Trong console, chạy:
const formData = new FormData();
formData.append('avatar', fileInput.files[0]);
formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

fetch('/personal/avatar-upload/', {
    method: 'POST',
    body: formData
}).then(response => response.json()).then(data => console.log(data));
```

## 📋 Checklist

- [ ] File input có hoạt động không?
- [ ] File được validate đúng không?
- [ ] Form submission có trigger không?
- [ ] Network request có được gửi không?
- [ ] Server có trả về response đúng không?
- [ ] Response có được parse đúng không?
- [ ] Avatar có được cập nhật không?

## 🎯 Kết quả mong đợi

1. **File selection**: Console log "File selected: File {...}"
2. **Form submission**: Console log "Form submitted"
3. **Network request**: POST request đến `/personal/avatar-upload/`
4. **Server response**: Status 200, JSON response với success: true
5. **Avatar update**: Page reload và hiển thị avatar mới

## 📞 Báo cáo lỗi

Nếu vẫn gặp vấn đề, hãy cung cấp:
1. Screenshot của console logs
2. Screenshot của Network tab
3. Mô tả chi tiết các bước đã thực hiện
4. Loại file và kích thước file đã test
