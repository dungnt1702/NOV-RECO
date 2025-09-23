# NOV-RECO Check-in System Test Suite

Comprehensive automated testing framework for all modules with automatic test execution on file changes.

## 📁 Structure

```
tests/
├── __init__.py                 # Test suite initialization
├── base.py                     # Base test class with common utilities
├── fixtures/                   # Test data and fixtures
│   ├── __init__.py
│   └── test_data_generator.py  # Comprehensive test data generator
├── utils/                      # Test utilities
│   ├── __init__.py
│   ├── test_runner.py          # Test execution runner
│   └── file_watcher.py         # File change watcher
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_users.py           # User module tests
│   ├── test_area.py            # Area module tests
│   └── test_checkin.py         # Checkin module tests
├── integration/                # Integration tests (future)
├── functional/                 # Functional tests (future)
└── requirements.txt            # Test dependencies
```

## 🚀 Quick Start

### 1. Setup Test Environment
```bash
python setup_tests.py
```

### 2. Generate Test Data
```bash
python run_tests.py generate
```

### 3. Run All Tests
```bash
python run_tests.py test
```

### 4. Run Module-Specific Tests
```bash
python run_tests.py module users
python run_tests.py module area
python run_tests.py module checkin
```

### 5. Watch for Changes (Auto-test)
```bash
python run_tests.py watch
# or
python tests/utils/file_watcher.py
```

## 🧪 Test Types

### Unit Tests
- **Location**: `tests/unit/`
- **Purpose**: Test individual components (models, views, forms, serializers)
- **Coverage**: Each module has comprehensive unit tests

### Integration Tests
- **Location**: `tests/integration/`
- **Purpose**: Test module interactions and API endpoints
- **Status**: Planned for future implementation

### Functional Tests
- **Location**: `tests/functional/`
- **Purpose**: Test complete user workflows
- **Status**: Planned for future implementation

## 📊 Test Data

The test suite includes comprehensive test data:

- **Users**: 15+ users with different roles (Admin, Manager, Employee)
- **Departments**: 5+ departments
- **Areas**: 7+ areas with different locations
- **Check-ins**: 300+ check-ins with realistic data

## 🔄 Automatic Testing

### File Watcher
The system automatically runs tests when files are modified:

1. **Monitors**: All Python files in the project
2. **Triggers**: On file save/modification
3. **Scope**: Runs tests for the specific module that changed
4. **Throttling**: Minimum 2-second interval between runs

### Module Detection
The watcher automatically detects which module changed:
- `apps/users/` → runs user module tests
- `apps/area/` → runs area module tests
- `apps/checkin/` → runs checkin module tests
- `tests/unit/test_*.py` → runs corresponding module tests

## 🛠️ Commands

### Main Commands
```bash
# Setup test environment
python setup_tests.py

# Generate test data
python run_tests.py generate

# Run all tests
python run_tests.py test

# Run specific module tests
python run_tests.py module <module_name>

# Watch for changes
python run_tests.py watch
```

### Test Runner Options
```bash
# Run unit tests only
python run_tests.py test --type unit

# Run integration tests only
python run_tests.py test --type integration

# Clean test data before running
python run_tests.py test --clean
```

## 📋 Test Coverage

### User Module (`test_users.py`)
- ✅ User model creation and validation
- ✅ User properties and methods
- ✅ Department model tests
- ✅ User views (list, create, edit)
- ✅ User forms validation
- ✅ User serializers

### Area Module (`test_area.py`)
- ✅ Area model creation and validation
- ✅ Area string representation
- ✅ Area views (list, create, edit)
- ✅ Area forms validation
- ✅ Area serializers

### Checkin Module (`test_checkin.py`)
- ✅ Checkin model creation and validation
- ✅ Checkin ordering and relationships
- ✅ Checkin views (action, history, list)
- ✅ Checkin forms validation
- ✅ Checkin serializers
- ✅ Checkin API endpoints

## 🔧 Configuration

### Test Settings
Tests use Django's test database and settings:
- **Database**: SQLite in-memory for speed
- **Media**: Temporary test media directory
- **Static**: Test static files
- **Debug**: Enabled for detailed error reporting

### Dependencies
Required packages for testing:
```
watchdog>=3.0.0      # File watching
coverage>=7.0.0      # Code coverage
pytest>=7.0.0        # Test framework
pytest-django>=4.5.0 # Django integration
factory-boy>=3.2.0   # Test data factories
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure Django is properly set up
   python manage.py check
   ```

2. **Test Data Issues**
   ```bash
   # Regenerate test data
   python run_tests.py generate
   ```

3. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x run_tests.py setup_tests.py
   ```

4. **Module Not Found**
   ```bash
   # Run from project root
   cd /path/to/checkin_project
   python run_tests.py test
   ```

### Debug Mode
Enable debug mode for detailed test output:
```bash
export DJANGO_DEBUG=True
python run_tests.py test
```

## 📈 Future Enhancements

### Planned Features
- [ ] Integration tests for API endpoints
- [ ] Functional tests for user workflows
- [ ] Performance tests for large datasets
- [ ] Visual regression tests for UI
- [ ] Load tests for concurrent users
- [ ] Mobile device testing
- [ ] Cross-browser compatibility tests

### Test Data Enhancements
- [ ] More realistic test data
- [ ] Edge case scenarios
- [ ] Performance test datasets
- [ ] Internationalization test data

## 🤝 Contributing

### Adding New Tests
1. Create test file in appropriate directory
2. Inherit from `TestBase` class
3. Follow naming convention: `test_<module>.py`
4. Add comprehensive test coverage
5. Update this README

### Test Guidelines
- Use descriptive test names
- Test both success and failure cases
- Include edge cases and validation
- Keep tests independent and isolated
- Use meaningful assertions
- Clean up test data in `tearDown()`

## 📞 Support

For test-related issues:
1. Check this README
2. Run `python run_tests.py test` to identify issues
3. Check Django logs for detailed errors
4. Verify test data with `python run_tests.py generate`
