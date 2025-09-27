"""
Unit tests for area module
Tests models, views, forms, and serializers
"""

import os
import sys

import django

# Add project root to Python path
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.area.forms import AreaForm
from apps.area.models import Area
from apps.area.serializers import AreaSerializer
from tests.base import TestBase


class AreaModelTest(TestBase):
    """Test Area model"""

    def test_area_creation(self):
        """Test area creation"""
        area = Area.objects.create(
            name="Test Area",
            description="Test area description",
            lat=10.762622,
            lng=106.660172,
            radius_m=100,
            is_active=True,
            created_by=self.test_data["admin_user"],
        )

        self.assertEqual(area.name, "Test Area")
        self.assertEqual(area.description, "Test area description")
        self.assertEqual(area.lat, 10.762622)
        self.assertEqual(area.lng, 106.660172)
        self.assertEqual(area.radius_m, 100)
        self.assertTrue(area.is_active)
        self.assertEqual(area.created_by, self.test_data["admin_user"])

    def test_area_str_representation(self):
        """Test area string representation"""
        area = self.test_data["test_area"]
        self.assertEqual(str(area), "Test Area")

    def test_area_validation(self):
        """Test area validation"""
        # Test invalid latitude
        with self.assertRaises(ValidationError):
            area = Area(
                name="Invalid Area",
                lat=200,  # Invalid latitude
                lng=106.660172,
                radius_m=100,
            )
            area.full_clean()

    def test_area_active_manager(self):
        """Test area active manager"""
        # Create inactive area
        inactive_area = Area.objects.create(
            name="Inactive Area",
            lat=10.762622,
            lng=106.660172,
            radius_m=100,
            is_active=False,
            created_by=self.test_data["admin_user"],
        )

        # Test active areas only
        active_areas = Area.objects.filter(is_active=True)
        self.assertIn(self.test_data["test_area"], active_areas)
        self.assertNotIn(inactive_area, active_areas)


class AreaViewsTest(TestBase):
    """Test area views"""

    def test_area_list_view_admin(self):
        """Test area list view as admin"""
        self.login_as("admin")
        response = self.client.get(reverse("area:list"))
        self.assert_response_ok(response)
        self.assert_contains(response, "Danh sách địa điểm")

    def test_area_list_view_unauthorized(self):
        """Test area list view without login"""
        response = self.client.get(reverse("area:list"))
        self.assert_response_redirect(response, 302)

    def test_area_create_view_admin(self):
        """Test area create view as admin"""
        self.login_as("admin")
        response = self.client.get(reverse("area:create"))
        self.assert_response_ok(response)
        self.assert_contains(response, "Tạo địa điểm mới")

    def test_area_create_post(self):
        """Test area create POST request"""
        self.login_as("admin")

        form_data = {
            "name": "New Test Area",
            "description": "New test area description",
            "lat": 10.800000,
            "lng": 106.700000,
            "radius_m": 150,
            "is_active": True,
        }

        response = self.client.post(reverse("area:create"), data=form_data)
        self.assert_response_redirect(response, 302)

        # Check if area was created
        self.assertTrue(Area.objects.filter(name="New Test Area").exists())


class AreaFormsTest(TestBase):
    """Test area forms"""

    def test_area_form_valid(self):
        """Test valid area form"""
        form_data = {
            "name": "Form Test Area",
            "description": "Form test area description",
            "lat": 10.750000,
            "lng": 106.650000,
            "radius_m": 120,
            "is_active": True,
        }

        form = AreaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_area_form_invalid(self):
        """Test invalid area form"""
        form_data = {
            "name": "",  # Empty name
            "description": "Invalid area",
            "lat": 200,  # Invalid latitude
            "lng": 106.650000,
            "radius_m": -50,  # Negative radius
            "is_active": True,
        }

        form = AreaForm(data=form_data)
        self.assertFalse(form.is_valid())


class AreaSerializersTest(TestBase):
    """Test area serializers"""

    def test_area_serializer(self):
        """Test area serializer"""
        area = self.test_data["test_area"]
        serializer = AreaSerializer(area)

        data = serializer.data
        self.assertEqual(data["name"], area.name)
        self.assertEqual(data["description"], area.description)
        self.assertEqual(data["lat"], area.lat)
        self.assertEqual(data["lng"], area.lng)
        self.assertEqual(data["radius_m"], area.radius_m)
        self.assertEqual(data["is_active"], area.is_active)

    def test_area_serializer_create(self):
        """Test area serializer create"""
        data = {
            "name": "Serializer Test Area",
            "description": "Serializer test area description",
            "lat": 10.780000,
            "lng": 106.680000,
            "radius_m": 130,
            "is_active": True,
        }

        serializer = AreaSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        area = serializer.save(created_by=self.test_data["admin_user"])
        self.assertEqual(area.name, "Serializer Test Area")
        self.assertEqual(area.created_by, self.test_data["admin_user"])
