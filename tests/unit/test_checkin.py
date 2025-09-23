"""
Unit tests for checkin module
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
from django.utils import timezone

from apps.checkin.models import Checkin
from apps.checkin.forms import CheckinForm
from apps.checkin.serializers import CheckinSerializer
from tests.base import TestBase


class CheckinModelTest(TestBase):
    """Test Checkin model"""
    
    def test_checkin_creation(self):
        """Test checkin creation"""
        checkin = Checkin.objects.create(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area'],
            lat=10.762622,
            lng=106.660172,
            photo='test_photos/test_checkin.jpg',
            note='Test checkin note',
            distance_m=50,
            ip='127.0.0.1',
            user_agent='Test User Agent'
        )
        
        self.assertEqual(checkin.user, self.test_data['employee_user'])
        self.assertEqual(checkin.area, self.test_data['test_area'])
        self.assertEqual(checkin.lat, 10.762622)
        self.assertEqual(checkin.lng, 106.660172)
        self.assertEqual(checkin.photo, 'test_photos/test_checkin.jpg')
        self.assertEqual(checkin.note, 'Test checkin note')
        self.assertEqual(checkin.distance_m, 50)
        self.assertEqual(checkin.ip, '127.0.0.1')
        self.assertEqual(checkin.user_agent, 'Test User Agent')
        
    def test_checkin_str_representation(self):
        """Test checkin string representation"""
        checkin = Checkin.objects.create(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area'],
            lat=10.762622,
            lng=106.660172
        )
        
        expected_str = f"Checkin by {self.test_data['employee_user'].username} at {self.test_data['test_area'].name}"
        self.assertEqual(str(checkin), expected_str)
        
    def test_checkin_ordering(self):
        """Test checkin ordering by created_at"""
        # Create checkins with different timestamps
        checkin1 = Checkin.objects.create(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area'],
            lat=10.762622,
            lng=106.660172,
            created_at=timezone.now()
        )
        
        checkin2 = Checkin.objects.create(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area'],
            lat=10.762622,
            lng=106.660172,
            created_at=timezone.now()
        )
        
        # Get checkins ordered by created_at desc
        checkins = Checkin.objects.all().order_by('-created_at')
        self.assertEqual(checkins[0], checkin2)  # Most recent first
        self.assertEqual(checkins[1], checkin1)


class CheckinViewsTest(TestBase):
    """Test checkin views"""
    
    def test_checkin_action_view_employee(self):
        """Test checkin action view as employee"""
        self.login_as('employee')
        response = self.client.get(reverse('checkin:action'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Check-in')
        
    def test_checkin_action_view_unauthorized(self):
        """Test checkin action view without login"""
        response = self.client.get(reverse('checkin:action'))
        self.assert_response_redirect(response, 302)
        
    def test_checkin_history_view_employee(self):
        """Test checkin history view as employee"""
        self.login_as('employee')
        response = self.client.get(reverse('checkin:history'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Lịch sử check-in')
        
    def test_checkin_list_view_admin(self):
        """Test checkin list view as admin"""
        self.login_as('admin')
        response = self.client.get(reverse('checkin:list'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Danh sách check-in')
        
    def test_checkin_submit_post(self):
        """Test checkin submit POST request"""
        self.login_as('employee')
        
        form_data = {
            'area': self.test_data['test_area'].id,
            'lat': 10.762622,
            'lng': 106.660172,
            'note': 'Test checkin submission',
            'photo': 'test_photos/submit_test.jpg'
        }
        
        response = self.client.post(reverse('checkin:submit'), data=form_data)
        self.assert_response_ok(response)
        
        # Check if checkin was created
        self.assertTrue(Checkin.objects.filter(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area']
        ).exists())


class CheckinFormsTest(TestBase):
    """Test checkin forms"""
    
    def test_checkin_form_valid(self):
        """Test valid checkin form"""
        form_data = {
            'area': self.test_data['test_area'].id,
            'lat': 10.762622,
            'lng': 106.660172,
            'note': 'Valid checkin form test',
            'photo': 'test_photos/valid_test.jpg'
        }
        
        form = CheckinForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_checkin_form_invalid(self):
        """Test invalid checkin form"""
        form_data = {
            'area': '',  # Empty area
            'lat': 200,  # Invalid latitude
            'lng': 106.660172,
            'note': 'Invalid checkin form test'
        }
        
        form = CheckinForm(data=form_data)
        self.assertFalse(form.is_valid())


class CheckinSerializersTest(TestBase):
    """Test checkin serializers"""
    
    def test_checkin_serializer(self):
        """Test checkin serializer"""
        checkin = Checkin.objects.create(
            user=self.test_data['employee_user'],
            area=self.test_data['test_area'],
            lat=10.762622,
            lng=106.660172,
            note='Serializer test checkin'
        )
        
        serializer = CheckinSerializer(checkin)
        data = serializer.data
        
        self.assertEqual(data['user'], checkin.user.id)
        self.assertEqual(data['area'], checkin.area.id)
        self.assertEqual(data['lat'], checkin.lat)
        self.assertEqual(data['lng'], checkin.lng)
        self.assertEqual(data['note'], checkin.note)
        
    def test_checkin_serializer_create(self):
        """Test checkin serializer create"""
        data = {
            'area': self.test_data['test_area'].id,
            'lat': 10.780000,
            'lng': 106.680000,
            'note': 'Serializer create test checkin',
            'photo': 'test_photos/serializer_test.jpg'
        }
        
        serializer = CheckinSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        checkin = serializer.save(user=self.test_data['employee_user'])
        self.assertEqual(checkin.user, self.test_data['employee_user'])
        self.assertEqual(checkin.area, self.test_data['test_area'])
        self.assertEqual(checkin.note, 'Serializer create test checkin')


class CheckinAPITest(TestBase):
    """Test checkin API endpoints"""
    
    def test_checkin_history_api(self):
        """Test checkin history API"""
        self.login_as('employee')
        response = self.client.get(reverse('checkin:history_api'))
        self.assert_response_ok(response)
        
        # Check response is JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
    def test_checkin_user_info_api(self):
        """Test checkin user info API"""
        self.login_as('employee')
        response = self.client.get(reverse('checkin:user_info_api'))
        self.assert_response_ok(response)
        
        # Check response is JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
    def test_checkin_list_api(self):
        """Test checkin list API"""
        self.login_as('admin')
        response = self.client.get(reverse('checkin:list_api'))
        self.assert_response_ok(response)
        
        # Check response is JSON
        self.assertEqual(response['Content-Type'], 'application/json')
