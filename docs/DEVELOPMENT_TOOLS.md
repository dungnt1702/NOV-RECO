# Django Development Tools

Tài liệu hướng dẫn sử dụng các công cụ development đã được cài đặt cho dự án Django.

## 📦 Các công cụ đã cài đặt

### 1. **Django Debug Toolbar**
- **Mục đích**: Debug và profiling Django applications
- **Tính năng**: 
  - SQL query analysis
  - Template debugging
  - Performance metrics
  - Request/response inspection
- **Cách sử dụng**: Tự động hiển thị khi `DEBUG=True`

### 2. **Django Extensions**
- **Mục đích**: Thêm các management commands hữu ích
- **Tính năng**:
  - `shell_plus`: Django shell với auto-imports
  - `runserver_plus`: Development server với Werkzeug debugger
  - `graph_models`: Tạo sơ đồ quan hệ models
- **Cách sử dụng**: `python manage.py <command>`

### 3. **pytest & pytest-django**
- **Mục đích**: Testing framework hiện đại
- **Tính năng**:
  - Test discovery tự động
  - Fixtures và parametrize
  - Coverage reports
  - Parallel testing
- **Cách sử dụng**: `pytest` hoặc `make test`

### 4. **Factory Boy**
- **Mục đích**: Tạo test data
- **Tính năng**:
  - Model factories
  - Faker integration
  - SubFactories
- **Cách sử dụng**: Tạo factories trong `tests/factories.py`

### 5. **Black (Code Formatter)**
- **Mục đích**: Tự động format Python code
- **Tính năng**:
  - Consistent code style
  - PEP 8 compliance
  - Configurable line length
- **Cách sử dụng**: `black .` hoặc `make format`

### 6. **Flake8 (Linter)**
- **Mục đích**: Code quality checking
- **Tính năng**:
  - Style checking
  - Error detection
  - Complexity analysis
- **Cách sử dụng**: `flake8 .` hoặc `make lint`

### 7. **isort (Import Sorter)**
- **Mục đích**: Sắp xếp imports
- **Tính năng**:
  - Group imports logically
  - Remove unused imports
  - Configurable sorting
- **Cách sử dụng**: `isort .` hoặc `make format`

## 🚀 Cách sử dụng

### Sử dụng Makefile (Khuyến nghị)

```bash
# Xem tất cả lệnh có sẵn
make help

# Format code
make format

# Lint code
make lint

# Chạy tests
make test

# Chạy tests với coverage
make test-cov

# Chạy tất cả code quality checks
make check

# Tạo sơ đồ models
make graph

# Khởi động Django shell
make shell

# Khởi động development server
make server

# Dọn dẹp temporary files
make clean
```

### Sử dụng Python script

```bash
# Sử dụng script dev_tools.py
python3 scripts/dev_tools.py format
python3 scripts/dev_tools.py lint
python3 scripts/dev_tools.py test
python3 scripts/dev_tools.py check
python3 scripts/dev_tools.py graph
python3 scripts/dev_tools.py shell
python3 scripts/dev_tools.py server
```

### Sử dụng trực tiếp

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Run tests
pytest

# Run tests with coverage
pytest --cov=apps --cov-report=html

# Django shell với extensions
python manage.py shell_plus

# Tạo model graph
python manage.py graph_models -a -o models.png
```

## ⚙️ Cấu hình

### 1. **Django Debug Toolbar**
- Tự động bật khi `DEBUG=True`
- URL: `http://localhost:3000/__debug__/`
- Panels: SQL, Templates, Performance, etc.

### 2. **pytest Configuration**
- File: `pytest.ini`
- Settings: `config.settings.test`
- Test paths: `apps/`

### 3. **Code Quality Tools**
- **Black**: `pyproject.toml`
- **Flake8**: `.flake8`
- **isort**: `.isort.cfg`

## 📁 Cấu trúc files

```
project/
├── config/settings/
│   ├── base.py          # Base settings với dev tools
│   └── test.py          # Test settings
├── scripts/
│   └── dev_tools.py     # Development tools script
├── tests/
│   └── factories.py     # Test data factories
├── pytest.ini          # pytest configuration
├── pyproject.toml       # Black & isort configuration
├── .flake8             # Flake8 configuration
├── .isort.cfg          # isort configuration
├── Makefile            # Development commands
└── requirements-dev.txt # Development dependencies
```

## 🧪 Testing

### Tạo test cases

```python
# apps/checkin/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Checkin

User = get_user_model()

class CheckinModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_checkin_creation(self):
        checkin = Checkin.objects.create(
            user=self.user,
            lat=10.762622,
            lng=106.660172,
            address='Test Address'
        )
        self.assertEqual(checkin.user, self.user)
```

### Chạy tests

```bash
# Chạy tất cả tests
pytest

# Chạy tests cho một app cụ thể
pytest apps/checkin/

# Chạy test cụ thể
pytest apps/checkin/tests.py::CheckinModelTest::test_checkin_creation

# Chạy tests với coverage
pytest --cov=apps --cov-report=html
```

## 🔧 Troubleshooting

### 1. **Django Debug Toolbar không hiển thị**
- Kiểm tra `DEBUG=True` trong settings
- Kiểm tra `INTERNAL_IPS` configuration
- Kiểm tra middleware order

### 2. **pytest không tìm thấy tests**
- Kiểm tra `pytest.ini` configuration
- Kiểm tra `DJANGO_SETTINGS_MODULE`
- Kiểm tra test file naming

### 3. **Flake8 báo lỗi**
- Chạy `black .` để format code
- Chạy `isort .` để sắp xếp imports
- Kiểm tra `.flake8` configuration

### 4. **Import errors trong tests**
- Kiểm tra `PYTHONPATH`
- Kiểm tra Django settings
- Kiểm tra app configuration

## 📚 Tài liệu tham khảo

- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Django Extensions](https://django-extensions.readthedocs.io/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [isort](https://pycqa.github.io/isort/)

## 🎯 Best Practices

1. **Luôn chạy code quality checks trước khi commit**
2. **Sử dụng factories thay vì tạo data thủ công trong tests**
3. **Viết tests cho tất cả models và views quan trọng**
4. **Sử dụng Django Debug Toolbar để debug performance issues**
5. **Format code thường xuyên với Black và isort**
6. **Sử dụng type hints và docstrings**
7. **Tạo model graphs để hiểu relationships**

## 🚀 Workflow Development

1. **Bắt đầu development**
   ```bash
   make server  # Khởi động server
   ```

2. **Trong quá trình development**
   ```bash
   make format  # Format code
   make lint    # Check code quality
   ```

3. **Trước khi commit**
   ```bash
   make check   # Chạy tất cả checks
   ```

4. **Khi cần debug**
   - Sử dụng Django Debug Toolbar
   - Sử dụng `make shell` để test code
   - Sử dụng `make graph` để hiểu model relationships

5. **Khi cần test**
   ```bash
   make test-cov  # Chạy tests với coverage
   ```
