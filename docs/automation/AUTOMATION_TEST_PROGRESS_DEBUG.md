# 🔧 Automation Test - Debug Progress Issue

## ❌ **Vấn đề đã gặp phải:**

### **Test Progress Không Chạy**
- **Vấn đề**: User báo "Tôi ko thấy test progress chạy"
- **Nguyên nhân có thể**: JavaScript không hoạt động, API không được gọi, hoặc UI không update
- **Kết quả**: Test progress không hiển thị, user không thấy tiến trình

## ✅ **Cách debug và sửa lỗi:**

### **1. Kiểm tra API Endpoints**

#### **API Start Test:**
```bash
# Test API start test
curl -b cookies.txt -X POST http://localhost:3000/automation-test/api/start-session/ \
  -H "Content-Type: application/json" \
  -d '{"notes": ""}'

# Kết quả: ✅ Hoạt động
{"success": true, "session_id": "9d3a7b03", "message": "Test started successfully"}
```

#### **API Status Check:**
```bash
# Test API status check
curl -b cookies.txt http://localhost:3000/automation-test/api/session-status/9d3a7b03/

# Kết quả: ✅ Hoạt động
{
  "success": true,
  "session": {
    "session_id": "9d3a7b03",
    "status": "running",
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "skipped_tests": 0,
    "duration": null,
    "success_rate": 0,
    "started_at": "2025-09-23T04:09:26.698557+00:00",
    "completed_at": null
  }
}
```

### **2. Kiểm tra JavaScript**

#### **File: `static/js/automation_test/dashboard.js`**

**Start Test Function:**
```javascript
function startTest() {
    // Disable button and show loading
    startTestBtn.disabled = true;
    startTestBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Starting...';
    
    fetch('/automation-test/api/start-session/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ notes: '' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentSessionId = data.session_id;
            showCurrentTestSection();
            startStatusCheck();
            showNotification('Test started successfully!', 'success');
        } else {
            showNotification('Error starting test: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error starting test: ' + error.message, 'error');
    })
    .finally(() => {
        // Re-enable button
        startTestBtn.disabled = false;
        startTestBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Test';
    });
}
```

**Status Check Function:**
```javascript
function startStatusCheck() {
    statusCheckInterval = setInterval(checkTestStatus, 2000); // Check every 2 seconds
}

function checkTestStatus() {
    if (!currentSessionId) return;

    fetch(`/automation-test/api/session-status/${currentSessionId}/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateTestStatus(data.session);
            
            // Stop checking if test is completed or failed
            if (data.session.status === 'completed' || data.session.status === 'failed') {
                stopStatusCheck();
                refreshPage();
            }
        }
    })
    .catch(error => {
        console.error('Error checking status:', error);
    });
}
```

### **3. Kiểm tra UI Elements**

#### **HTML Template: `templates/automation_test/dashboard.html`**

**Start Test Button:**
```html
<button id="startTestBtn" class="btn btn-primary btn-lg">
    <i class="fas fa-play me-2"></i>Start Test
</button>
```

**Current Test Section:**
```html
<div id="currentTestSection" class="test-progress-card" style="display: none;">
    <div class="progress-section">
        <div class="progress-label">
            <h4>Test Execution in Progress</h4>
            <p>Session ID: <span id="currentSessionId">-</span></p>
        </div>
        
        <div class="progress-details">
            <div class="progress-stat">
                <span class="stat-number" id="currentPassed">0</span>
                <span class="stat-label">Passed</span>
            </div>
            <div class="progress-stat">
                <span class="stat-number" id="currentFailed">0</span>
                <span class="stat-label">Failed</span>
            </div>
            <div class="progress-stat">
                <span class="stat-number" id="currentSkipped">0</span>
                <span class="stat-label">Skipped</span>
            </div>
        </div>
        
        <div class="test-visual">
            <div class="progress-bar-container">
                <div class="progress-bar" role="progressbar" style="width: 0%" 
                     aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" id="progressBar">
                </div>
            </div>
            
            <div class="progress-circle-container">
                <div class="progress-circle" id="circularProgress">
                    <span class="progress-text" id="circularProgressText">0%</span>
                </div>
            </div>
        </div>
        
        <div class="test-status">
            <span class="badge badge-warning" id="currentStatus">Running</span>
        </div>
    </div>
</div>
```

### **4. Debug Steps**

#### **Bước 1: Kiểm tra Console Errors**
```javascript
// Mở browser console (F12)
// Kiểm tra có lỗi JavaScript nào không
// Tìm các lỗi như:
// - Uncaught ReferenceError
// - Uncaught TypeError
// - Network errors
// - CORS errors
```

#### **Bước 2: Kiểm tra Network Tab**
```javascript
// Mở Network tab trong DevTools
// Click "Start Test" button
// Kiểm tra:
// - POST /automation-test/api/start-session/ có được gọi không?
// - Response status code là gì?
// - Response data có đúng không?
// - GET /automation-test/api/session-status/ có được gọi không?
```

#### **Bước 3: Kiểm tra JavaScript Functions**
```javascript
// Trong console, test các functions:
console.log('Testing startTest function...');
startTest();

console.log('Testing checkTestStatus function...');
checkTestStatus();

console.log('Testing updateTestStatus function...');
updateTestStatus({
    session_id: 'test123',
    status: 'running',
    total_tests: 10,
    passed_tests: 5,
    failed_tests: 2,
    skipped_tests: 3
});
```

### **5. Các vấn đề có thể gặp**

#### **Vấn đề 1: CSRF Token**
```javascript
// Lỗi: CSRF verification failed
// Sửa: Đảm bảo getCookie('csrftoken') hoạt động
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

#### **Vấn đề 2: Authentication**
```javascript
// Lỗi: 403 Forbidden hoặc 302 Redirect
// Sửa: Đảm bảo user đã login
// Kiểm tra session cookie trong browser
```

#### **Vấn đề 3: JavaScript Errors**
```javascript
// Lỗi: Uncaught ReferenceError
// Sửa: Đảm bảo tất cả functions được định nghĩa
// Kiểm tra syntax errors
```

#### **Vấn đề 4: UI Not Updating**
```javascript
// Lỗi: Progress bar không update
// Sửa: Kiểm tra updateTestStatus function
// Đảm bảo DOM elements tồn tại
```

### **6. Test Script**

#### **Manual Test:**
```javascript
// 1. Mở browser console
// 2. Chạy các lệnh sau:

// Test start test
fetch('/automation-test/api/start-session/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ notes: '' })
})
.then(response => response.json())
.then(data => {
    console.log('Start test result:', data);
    if (data.success) {
        // Test status check
        fetch(`/automation-test/api/session-status/${data.session_id}/`)
        .then(response => response.json())
        .then(statusData => {
            console.log('Status check result:', statusData);
        });
    }
});
```

### **7. Expected Behavior**

#### **Khi Click "Start Test":**
1. Button chuyển thành "Starting..." với spinner
2. API call đến `/automation-test/api/start-session/`
3. Nếu thành công:
   - Hiển thị "Test Execution in Progress" section
   - Bắt đầu status check mỗi 2 giây
   - Hiển thị notification "Test started successfully!"
4. Button trở lại "Start Test"

#### **Khi Test Running:**
1. Progress bar update real-time
2. Circular progress update
3. Statistics update (Passed, Failed, Skipped)
4. Status badge hiển thị "Running"

#### **Khi Test Completed:**
1. Status badge chuyển thành "Completed"
2. Progress bar đạt 100%
3. Dừng status check
4. Refresh page để hiển thị kết quả

## 🎯 **Truy cập để test:**

### **URL:**
```
http://localhost:3000/automation-test/
```

### **Login Credentials:**
```
Username: admin
Password: admin123
```

### **Test Steps:**
1. Mở browser và truy cập URL
2. Login với credentials
3. Click "Start Test" button
4. Quan sát progress bar và statistics
5. Kiểm tra browser console cho errors

## 🚀 **Kết quả mong đợi:**

- ✅ **API hoạt động**: Start test và status check APIs trả về đúng
- ✅ **JavaScript hoạt động**: Không có lỗi console
- ✅ **UI update**: Progress bar và statistics update real-time
- ✅ **User experience**: Smooth và responsive

Bây giờ hãy test trong browser để xem có vấn đề gì! 🎉✨
