"""
Test configuration settings
Centralized configuration for all test activities
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
APPS_DIR = PROJECT_ROOT / "apps"
TESTS_DIR = PROJECT_ROOT / "tests"
UNIT_TESTS_DIR = TESTS_DIR / "unit"
INTEGRATION_TESTS_DIR = TESTS_DIR / "integration"
FUNCTIONAL_TESTS_DIR = TESTS_DIR / "functional"

# Test settings
TEST_SETTINGS = {
    "DATABASE": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "MEDIA_ROOT": TESTS_DIR / "media",
    "STATIC_ROOT": TESTS_DIR / "static",
    "DEBUG": True,
    "SECRET_KEY": "test-secret-key-for-testing-only",
}

# Test data settings
TEST_DATA = {
    "USERS": {
        "ADMIN_COUNT": 2,
        "MANAGER_COUNT": 3,
        "EMPLOYEE_COUNT": 10,
    },
    "DEPARTMENTS": {
        "COUNT": 5,
        "NAMES": [
            "Phòng Hành chính",
            "Phòng IT",
            "Phòng Kinh doanh",
            "Phòng Nhân sự",
            "Phòng Kế toán",
        ],
    },
    "AREAS": {
        "COUNT": 7,
        "LOCATIONS": [
            {
                "name": "Văn phòng chính",
                "lat": 10.762622,
                "lng": 106.660172,
                "radius": 50,
            },
            {
                "name": "Chi nhánh Quận 1",
                "lat": 10.7769,
                "lng": 106.7009,
                "radius": 100,
            },
            {"name": "Chi nhánh Quận 7", "lat": 10.7329, "lng": 106.7229, "radius": 80},
            {
                "name": "Kho hàng Bình Dương",
                "lat": 10.9804,
                "lng": 106.6519,
                "radius": 200,
            },
            {
                "name": "Showroom Đồng Nai",
                "lat": 10.9447,
                "lng": 106.8243,
                "radius": 150,
            },
            {
                "name": "Văn phòng đại diện Hà Nội",
                "lat": 21.0285,
                "lng": 105.8542,
                "radius": 120,
            },
            {
                "name": "Trung tâm đào tạo",
                "lat": 10.7626,
                "lng": 106.6601,
                "radius": 60,
            },
        ],
    },
    "CHECKINS": {
        "COUNT": 300,
        "DAYS_BACK": 30,
    },
}

# File watching settings
WATCH_SETTINGS = {
    "MIN_INTERVAL": 3,  # seconds
    "TIMEOUT": 120,  # seconds
    "IGNORED_DIRS": {
        ".git",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        "venv",
        "static",
        "media",
    },
    "IGNORED_FILES": {".DS_Store", "*.pyc", "*.pyo", "*.log", "*.tmp"},
    "WATCH_EXTENSIONS": {".py"},
}

# Test execution settings
EXECUTION_SETTINGS = {
    "PARALLEL": False,
    "VERBOSE": 2,
    "KEEP_DB": True,
    "FAILFAST": False,
    "COVERAGE": True,
    "COVERAGE_HTML": True,
    "COVERAGE_REPORT": "html",
}

# Module detection patterns
MODULE_PATTERNS = {
    "APPS_DIR": "apps",
    "TESTS_DIR": "tests",
    "UNIT_TESTS": "unit",
    "INTEGRATION_TESTS": "integration",
    "FUNCTIONAL_TESTS": "functional",
}

# Test file templates
TEST_TEMPLATES = {
    "UNIT_TEST": '''"""
Unit tests for {module_name} module
Tests models, views, forms, and serializers
"""

import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError

from .base import TestBase


class {ModuleName}ModelTest(TestBase):
    """Test {module_name} models"""
    
    def test_model_creation(self):
        """Test model creation"""
        # TODO: Implement model creation tests
        pass
        
    def test_model_validation(self):
        """Test model validation"""
        # TODO: Implement model validation tests
        pass


class {ModuleName}ViewsTest(TestBase):
    """Test {module_name} views"""
    
    def test_view_access(self):
        """Test view access"""
        # TODO: Implement view access tests
        pass
        
    def test_view_permissions(self):
        """Test view permissions"""
        # TODO: Implement view permission tests
        pass


class {ModuleName}FormsTest(TestBase):
    """Test {module_name} forms"""
    
    def test_form_validation(self):
        """Test form validation"""
        # TODO: Implement form validation tests
        pass


class {ModuleName}SerializersTest(TestBase):
    """Test {module_name} serializers"""
    
    def test_serializer_serialization(self):
        """Test serializer serialization"""
        # TODO: Implement serializer tests
        pass
''',
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": TESTS_DIR / "test.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "tests": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Environment variables
ENV_VARS = {
    "DJANGO_SETTINGS_MODULE": "config.settings",
    "DJANGO_ENVIRONMENT": "test",
    "PYTHONPATH": str(PROJECT_ROOT),
}


def get_test_settings():
    """Get test settings for Django"""
    return TEST_SETTINGS


def get_test_data_config():
    """Get test data configuration"""
    return TEST_DATA


def get_watch_settings():
    """Get file watching settings"""
    return WATCH_SETTINGS


def get_execution_settings():
    """Get test execution settings"""
    return EXECUTION_SETTINGS


def get_module_patterns():
    """Get module detection patterns"""
    return MODULE_PATTERNS


def get_test_template(template_name):
    """Get test file template"""
    return TEST_TEMPLATES.get(template_name, "")


def get_logging_config():
    """Get logging configuration"""
    return LOGGING_CONFIG


def get_env_vars():
    """Get environment variables"""
    return ENV_VARS
