# Automation Test Module

## Overview

The Automation Test module provides comprehensive testing capabilities for the NOV-RECO Check-in System, including display tests, link tests, and comprehensive functionality tests.

## Features

### Test Types

1. **Display Tests** - Tests UI elements and page displays
2. **Link Tests** - Tests navigation and link functionality  
3. **Comprehensive Tests** - Combines all test types plus system integration tests
4. **Django Unit Tests** - Traditional Django test suite

### Test Modules

- **DisplayTestModule**: Tests page displays, responsive design, static files
- **LinkTestModule**: Tests navigation, forms, API endpoints
- **ComprehensiveTestModule**: Full system testing including performance and security

## Usage

### Web Interface

1. Navigate to `/automation-test/`
2. Select test type from dropdown:
   - Display Tests
   - Link Tests  
   - Comprehensive Tests
   - Django Unit Tests
3. Click "Start Test" button
4. Monitor progress in real-time
5. View detailed results and logs

### Command Line

```bash
# Run comprehensive tests (default)
python run_automation_tests.py

# Run specific test type
python run_automation_tests.py --type display
python run_automation_tests.py --type links
python run_automation_tests.py --type comprehensive

# Run Django unit tests
python run_automation_tests.py --django tests.unit.test_users

# Run all tests
python run_automation_tests.py --all

# Specify custom URL
python run_automation_tests.py --url http://localhost:8000
```

### Programmatic Usage

```python
from apps.automation_test.test_modules import run_test_module

# Run display tests
results = run_test_module('display')

# Run comprehensive tests
results = run_test_module('comprehensive')
```

## Test Results

Each test returns:
- `total_tests`: Total number of tests run
- `passed`: Number of passed tests
- `failed`: Number of failed tests
- `skipped`: Number of skipped tests
- `errors`: List of error messages
- `detailed_results`: Detailed test results

## Integration with Existing Tests

The module integrates with the existing `tests/` directory structure:

- **Unit Tests**: `tests/unit/` - Individual component tests
- **Integration Tests**: `tests/integration/` - Component interaction tests
- **Functional Tests**: `tests/functional/` - End-to-end workflow tests

## Configuration

### Environment Variables

- `DJANGO_ENVIRONMENT`: Set to 'local', 'test', or 'production'
- `TEST_BASE_URL`: Base URL for testing (default: http://localhost:3000)

### Settings

The module uses Django's test framework and respects:
- `TEST_RUNNER` setting
- Database configuration for test environment
- Static file settings

## API Endpoints

- `POST /automation-test/api/start-session/` - Start new test session
- `GET /automation-test/api/session-status/<session_id>/` - Get session status
- `GET /automation-test/api/session-logs/<session_id>/` - Get session logs

## Permissions

- **Admin**: Full access to all test types
- **Manager**: Access to display and link tests
- **Employee**: Read-only access to test results

## Monitoring

The web interface provides:
- Real-time progress updates
- Test checklist with status indicators
- Detailed logs and error messages
- Session history and statistics
- Export capabilities for test results

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Kill existing Django processes
2. **Database Errors**: Ensure test database is properly configured
3. **Static Files**: Run `python manage.py collectstatic`
4. **Permissions**: Ensure user has appropriate role

### Debug Mode

Enable debug mode by setting `DEBUG=True` in settings for detailed error information.

## Contributing

When adding new tests:

1. Add test methods to appropriate module class
2. Update test results format if needed
3. Add test type to dropdown menu
4. Update documentation

## Future Enhancements

- Performance benchmarking
- Security vulnerability scanning
- Cross-browser testing
- Mobile device testing
- API load testing
