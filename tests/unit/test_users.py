"""
Unit tests for users module
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
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.users.models import User, UserRole, Department
from apps.users.forms import UserCreateForm, UserUpdateForm, DepartmentForm
from apps.users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from tests.base import TestBase


class UserModelTest(TestBase):
    """Test User model"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=UserRole.EMPLOYEE
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, UserRole.EMPLOYEE)
        self.assertTrue(user.check_password('testpass123'))
        
    def test_user_properties(self):
        """Test user properties"""
        user = self.test_data['admin_user']
        
        self.assertTrue(user.is_admin_user)
        self.assertFalse(user.is_manager_user)
        self.assertFalse(user.is_employee_user)
        self.assertEqual(user.full_name, 'Test Admin')
        self.assertEqual(user.get_display_name(), 'Test Admin')
        
    def test_user_str_representation(self):
        """Test user string representation"""
        user = self.test_data['admin_user']
        self.assertEqual(str(user), 'test_admin')


class DepartmentModelTest(TestBase):
    """Test Department model"""
    
    def test_department_creation(self):
        """Test department creation"""
        dept = Department.objects.create(
            name='Test Department',
            description='Test department description'
        )
        
        self.assertEqual(dept.name, 'Test Department')
        self.assertEqual(dept.description, 'Test department description')
        
    def test_department_str_representation(self):
        """Test department string representation"""
        dept = self.test_data['test_department']
        self.assertEqual(str(dept), 'Test Department')


class UserViewsTest(TestBase):
    """Test user views"""
    
    def test_user_list_view_admin(self):
        """Test user list view as admin"""
        self.login_as('admin')
        response = self.client.get(reverse('users:list'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Danh sách người dùng')
        
    def test_user_list_view_unauthorized(self):
        """Test user list view without login"""
        response = self.client.get(reverse('users:list'))
        self.assert_response_redirect(response, 302)
        
    def test_user_create_view_admin(self):
        """Test user create view as admin"""
        self.login_as('admin')
        response = self.client.get(reverse('users:create'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Tạo người dùng mới')
        
    def test_department_list_view(self):
        """Test department list view"""
        self.login_as('admin')
        response = self.client.get(reverse('users:departments'))
        self.assert_response_ok(response)
        self.assert_contains(response, 'Danh sách phòng ban')


class UserFormsTest(TestBase):
    """Test user forms"""
    
    def test_user_create_form_valid(self):
        """Test valid user create form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': UserRole.EMPLOYEE,
            'department': self.test_data['test_department'].id
        }
        
        form = UserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_create_form_invalid(self):
        """Test invalid user create form"""
        form_data = {
            'username': '',  # Empty username
            'email': 'invalid-email',  # Invalid email
            'first_name': 'New',
            'last_name': 'User',
            'role': UserRole.EMPLOYEE
        }
        
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_department_form_valid(self):
        """Test valid department form"""
        form_data = {
            'name': 'New Department',
            'description': 'New department description'
        }
        
        form = DepartmentForm(data=form_data)
        self.assertTrue(form.is_valid())


class UserSerializersTest(TestBase):
    """Test user serializers"""
    
    def test_user_serializer(self):
        """Test user serializer"""
        user = self.test_data['admin_user']
        serializer = UserSerializer(user)
        
        data = serializer.data
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['role'], user.role)
        
    def test_user_create_serializer(self):
        """Test user create serializer"""
        data = {
            'username': 'serializeruser',
            'email': 'serializer@example.com',
            'first_name': 'Serializer',
            'last_name': 'User',
            'role': UserRole.EMPLOYEE,
            'department': self.test_data['test_department'].id
        }
        
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'serializeruser')
        self.assertEqual(user.email, 'serializer@example.com')
