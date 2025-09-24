# 🤖 Automation Test Module

Module automation test cho hệ thống NOV-RECO Check-in, cung cấp giao diện web để chạy test tự động và xem báo cáo kết quả.

## 🚀 Tính năng

### ✨ Giao diện Web
- **Dashboard**: Tổng quan về các test session, thống kê thành công/thất bại
- **Test Execution**: Chạy test với một click, theo dõi tiến trình real-time
- **Session Detail**: Xem chi tiết kết quả test, logs, và lỗi
- **Log Viewer**: Xem logs với filter theo level, search, export

### 🔧 Chức năng chính
- **One-Click Testing**: Chỉ cần bấm 1 nút để chạy toàn bộ test suite
- **Real-time Monitoring**: Theo dõi tiến trình test real-time
- **Comprehensive Logging**: Ghi lại tất cả logs và lỗi chi tiết
- **Test Results**: Lưu trữ kết quả test với thống kê đầy đủ
- **Export Functionality**: Export logs và báo cáo test

## 📁 Cấu trúc Module

```
apps/automation_test/
├── __init__.py
├── apps.py
├── models.py          # TestSession, TestResult, TestLog
├── views.py           # Dashboard, execution, monitoring
├── urls.py            # URL patterns
├── admin.py           # Django admin interface
└── migrations/        # Database migrations

templates/automation_test/
├── dashboard.html     # Main dashboard
└── session_detail.html # Test session details

static/css/automation_test/
├── dashboard.css      # Dashboard styles
└── session_detail.css # Session detail styles

static/js/automation_test/
├── dashboard.js       # Dashboard functionality
└── session_detail.js  # Session detail functionality
```

## 🗄️ Database Models

### TestSession
- `session_id`: ID duy nhất của test session
- `user`: User thực hiện test
- `status`: Trạng thái (running, completed, failed, cancelled)
- `started_at`: Thời gian bắt đầu
- `completed_at`: Thời gian hoàn thành
- `total_tests`: Tổng số test
- `passed_tests`: Số test pass
- `failed_tests`: Số test fail
- `skipped_tests`: Số test skip
- `duration`: Thời gian thực hiện (giây)
- `notes`: Ghi chú

### TestResult
- `session`: Liên kết với TestSession
- `test_name`: Tên test
- `module`: Module chứa test
- `status`: Kết quả (passed, failed, skipped, error)
- `duration`: Thời gian thực hiện test
- `error_message`: Thông báo lỗi
- `stack_trace`: Stack trace lỗi

### TestLog
- `session`: Liên kết với TestSession
- `level`: Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: Nội dung log
- `timestamp`: Thời gian
- `test_name`: Tên test liên quan

## 🌐 URL Patterns

```
/automation-test/                    # Dashboard
/automation-test/session/<id>/       # Session detail
/automation-test/start/              # Start test (POST)
/automation-test/status/<id>/        # Get status (API)
/automation-test/logs/<id>/          # Get logs (API)
```

## 🔐 Permissions

- **Admin**: Full access
- **Manager**: Full access  
- **Employee**: No access (có thể mở rộng sau)

## 🚀 Cách sử dụng

### 1. Truy cập Dashboard
```
http://localhost:3000/automation-test/
```

### 2. Chạy Test
1. Bấm nút "Start Test"
2. Thêm ghi chú (tùy chọn)
3. Bấm "Start Test" để bắt đầu
4. Theo dõi tiến trình real-time

### 3. Xem Kết quả
- Dashboard hiển thị danh sách các test session
- Click vào Session ID để xem chi tiết
- Xem logs, lỗi, và thống kê

### 4. Export Logs
- Trong session detail, bấm "Export Logs"
- File .txt sẽ được tải về

## 🔧 API Endpoints

### Start Test
```http
POST /automation-test/start/
Content-Type: application/x-www-form-urlencoded

notes=Optional test notes
```

### Get Status
```http
GET /automation-test/status/<session_id>/
```

### Get Logs
```http
GET /automation-test/logs/<session_id>/
```

## 🎨 Giao diện

### Dashboard
- **Statistics Cards**: Tổng sessions, completed, failed, success rate
- **Current Test**: Hiển thị test đang chạy với progress bar
- **Recent Sessions**: Bảng danh sách các session gần đây
- **Recent Results**: Bảng kết quả test gần đây

### Session Detail
- **Session Info**: Thông tin chi tiết session
- **Success Rate**: Biểu đồ tròn hiển thị tỷ lệ thành công
- **Test Results**: Bảng kết quả từng test
- **Test Logs**: Logs với filter và search

## 🔄 Tích hợp với Test System

Module này tích hợp với hệ thống test hiện có:

```python
# Chạy test từ command line
python test.py run

# Chạy test từ web interface
# Truy cập /automation-test/ và bấm "Start Test"
```

## 📊 Monitoring

- **Real-time Updates**: Dashboard tự động cập nhật mỗi 2 giây
- **Progress Tracking**: Hiển thị tiến trình test real-time
- **Auto-refresh**: Tự động refresh khi test hoàn thành
- **Notifications**: Thông báo khi test bắt đầu/kết thúc

## 🛠️ Development

### Thêm Test Module mới
1. Tạo test trong `tests/unit/test_<module>.py`
2. Module sẽ tự động được phát hiện và chạy

### Customize Logging
```python
# Trong test code
from apps.automation_test.models import TestLog

TestLog.objects.create(
    session=session,
    level='INFO',
    message='Custom log message',
    test_name='my_test'
)
```

### Customize Test Results
```python
# Trong test code
from apps.automation_test.models import TestResult

TestResult.objects.create(
    session=session,
    test_name='my_test',
    module='my_module',
    status='passed',
    duration=1.5
)
```

## 🎯 Lợi ích

1. **Dễ sử dụng**: Chỉ cần 1 click để chạy test
2. **Trực quan**: Giao diện web đẹp, dễ theo dõi
3. **Chi tiết**: Logs và báo cáo đầy đủ
4. **Linh hoạt**: Có thể mở rộng và tùy chỉnh
5. **Tích hợp**: Hoạt động với hệ thống test hiện có
6. **Monitoring**: Theo dõi real-time, không cần command line

## 🔮 Tương lai

- [ ] Email notifications khi test fail
- [ ] Scheduled testing
- [ ] Test comparison
- [ ] Performance metrics
- [ ] Integration với CI/CD
- [ ] Mobile app support
