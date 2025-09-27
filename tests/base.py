"""
Base test class for all module tests
Provides common functionality and setup
"""

import os
import sys

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction
from django.test import Client, TestCase

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.area.models import Area
from apps.checkin.models import Checkin
from apps.users.models import Department, User, UserRole


class TestBase(TestCase):
    """Base test class with common setup and utilities"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.test_data = {}

    def setUp(self):
        """Set up test data for each test"""
        self.create_test_data()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up test data
        Checkin.objects.all().delete()
        User.objects.filter(username__startswith="test_").delete()
        Area.objects.filter(name__startswith="Test").delete()
        Department.objects.filter(name__startswith="Test").delete()

    def create_test_data(self):
        """Create basic test data"""
        # Create test department
        self.test_department, _ = Department.objects.get_or_create(
            name="Test Department",
            defaults={"description": "Test department for testing"},
        )

        # Create test admin user
        self.admin_user, _ = User.objects.get_or_create(
            username="test_admin",
            defaults={
                "email": "admin@test.com",
                "first_name": "Test",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "department": self.test_department,
            },
        )
        self.admin_user.set_password("testpass123")
        self.admin_user.save()

        # Create test manager user
        self.manager_user, _ = User.objects.get_or_create(
            username="test_manager",
            defaults={
                "email": "manager@test.com",
                "first_name": "Test",
                "last_name": "Manager",
                "role": UserRole.MANAGER,
                "department": self.test_department,
            },
        )
        self.manager_user.set_password("testpass123")
        self.manager_user.save()

        # Create test employee user
        self.employee_user, _ = User.objects.get_or_create(
            username="test_employee",
            defaults={
                "email": "employee@test.com",
                "first_name": "Test",
                "last_name": "Employee",
                "role": UserRole.EMPLOYEE,
                "department": self.test_department,
            },
        )
        self.employee_user.set_password("testpass123")
        self.employee_user.save()

        # Create test area
        self.test_area, _ = Area.objects.get_or_create(
            name="Test Area",
            defaults={
                "description": "Test area for testing",
                "lat": 10.762622,
                "lng": 106.660172,
                "radius_m": 100,
                "is_active": True,
                "created_by": self.admin_user,
            },
        )

        self.test_data = {
            "admin_user": self.admin_user,
            "manager_user": self.manager_user,
            "employee_user": self.employee_user,
            "test_department": self.test_department,
            "test_area": self.test_area,
        }

    def login_as(self, user_type="admin"):
        """Login as specific user type"""
        user = self.test_data.get(f"{user_type}_user")
        if user:
            self.client.force_login(user)
        return user

    def assert_response_ok(self, response, expected_status=200):
        """Assert response is OK with expected status"""
        self.assertEqual(response.status_code, expected_status)

    def assert_response_redirect(self, response, expected_status=302):
        """Assert response is redirect with expected status"""
        self.assertEqual(response.status_code, expected_status)

    def assert_contains(self, response, text):
        """Assert response contains specific text"""
        self.assertContains(response, text)

    def assert_not_contains(self, response, text):
        """Assert response does not contain specific text"""
        self.assertNotContains(response, text)
