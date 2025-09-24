# 🧪 Testing Documentation

Tài liệu testing hệ thống NOV-RECO.

## 📄 Files

- **`README.md`** - Hướng dẫn testing tổng quan

## 🎯 Nội dung

### Testing Overview
- Unit testing
- Integration testing
- Functional testing
- Performance testing
- Security testing

### Test Types
- **Unit Tests** - Test individual components
- **Integration Tests** - Test component interactions
- **Functional Tests** - Test user workflows
- **API Tests** - Test REST API endpoints
- **Permission Tests** - Test permission system

### Test Commands
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Data
- Sample users
- Test departments
- Test areas
- Test check-ins

## 🔗 Liên kết

- [Tài liệu chính](../README.md)
- [Hướng dẫn phát triển](../development/DEVELOPMENT.md)
- [Automation Testing](../automation/README.md)