"""
Test cases for checkin app
"""

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.location.models import Location

from .models import Checkin, Checkout

User = get_user_model()


class CheckinModelTest(TestCase):
    """Test cases for Checkin model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.location = Location.objects.create(
            name="Test Location",
            lat=10.762622,
            lng=106.660172,
            radius_m=100,
            is_active=True,
        )

    def test_checkin_creation(self):
        """Test creating a checkin"""
        checkin = Checkin.objects.create(
            user=self.user,
            location=self.location,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
            note="Test note",
            checkin_type="in",
        )

        self.assertEqual(checkin.user, self.user)
        self.assertEqual(checkin.location, self.location)
        self.assertEqual(checkin.checkin_type, "in")
        self.assertEqual(checkin.note, "Test note")

    def test_checkin_str_representation(self):
        """Test string representation of checkin"""
        checkin = Checkin.objects.create(
            user=self.user,
            location=self.location,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
        )

        expected = f"{self.user.get_full_name()} - {checkin.created_at.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(checkin), expected)

    def test_checkin_type_choices(self):
        """Test checkin type choices"""
        checkin = Checkin.objects.create(
            user=self.user,
            location=self.location,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
            checkin_type="in",
        )

        self.assertEqual(checkin.get_checkin_type_display(), "Check-in")


class CheckoutModelTest(TestCase):
    """Test cases for Checkout model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.location = Location.objects.create(
            name="Test Location",
            lat=10.762622,
            lng=106.660172,
            radius_m=100,
            is_active=True,
        )

        self.checkin = Checkin.objects.create(
            user=self.user,
            location=self.location,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
            checkin_type="in",
        )

    def test_checkout_creation(self):
        """Test creating a checkout"""
        checkout = Checkout.objects.create(
            user=self.user,
            checkin=self.checkin,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
            note="Test checkout note",
        )

        self.assertEqual(checkout.user, self.user)
        self.assertEqual(checkout.checkin, self.checkin)
        self.assertEqual(checkout.note, "Test checkout note")

    def test_checkout_str_representation(self):
        """Test string representation of checkout"""
        checkout = Checkout.objects.create(
            user=self.user,
            checkin=self.checkin,
            lat=10.762622,
            lng=106.660172,
            address="Test Address",
        )

        expected = f"{self.user.get_full_name()} - {checkout.created_at.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(checkout), expected)


class CheckinViewsTest(TestCase):
    """Test cases for checkin views"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_checkin_action_view_requires_login(self):
        """Test that checkin action view requires login"""
        response = self.client.get(reverse("checkin:action"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_checkin_action_view_with_login(self):
        """Test checkin action view with logged in user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("checkin:action"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check-in")

    def test_checkin_history_view_requires_login(self):
        """Test that checkin history view requires login"""
        response = self.client.get(reverse("checkin:history"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_checkin_history_view_with_login(self):
        """Test checkin history view with logged in user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("checkin:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lịch sử Check-in")


class CheckinUtilsTest(TestCase):
    """Test cases for checkin utilities"""

    def setUp(self):
        """Set up test data"""
        self.location = Location.objects.create(
            name="Test Location",
            lat=10.762622,
            lng=106.660172,
            radius_m=100,
            is_active=True,
        )

    def test_haversine_distance_calculation(self):
        """Test haversine distance calculation"""
        from .utils import haversine_distance

        # Distance between two points in Ho Chi Minh City
        lat1, lng1 = 10.762622, 106.660172  # District 1
        lat2, lng2 = 10.7769, 106.7009  # District 3

        distance = haversine_distance(lat1, lng1, lat2, lng2)

        # Should be approximately 5-6 km
        self.assertGreater(distance, 4000)  # More than 4km
        self.assertLess(distance, 8000)  # Less than 8km

    def test_find_best_location_for_checkin(self):
        """Test finding best location for checkin"""
        from .utils import find_best_location_for_checkin

        # Test with coordinates within radius
        lat, lng = 10.762622, 106.660172  # Same as location
        location_name, distance = find_best_location_for_checkin(lat, lng)

        self.assertEqual(location_name, "Test Location")
        self.assertLess(distance, 100)  # Within radius

        # Test with coordinates outside radius
        lat, lng = 10.800000, 106.700000  # Far from location
        location_name, distance = find_best_location_for_checkin(lat, lng)

        self.assertEqual(location_name, "Không xác định")
        self.assertIsNone(distance)
