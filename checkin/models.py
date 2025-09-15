from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied

# User Roles
class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    MANAGER = 'manager', 'Quản lý'
    EMPLOYEE = 'employee', 'Nhân viên'

# Custom User Model
class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        help_text="Vai trò của người dùng trong hệ thống"
    )
    phone = models.CharField(max_length=15, blank=True, help_text="Số điện thoại")
    department = models.CharField(max_length=100, blank=True, help_text="Phòng ban")
    employee_id = models.CharField(max_length=20, blank=True, unique=True, help_text="Mã nhân viên")
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_manager(self):
        return self.role == UserRole.MANAGER
    
    def is_employee(self):
        return self.role == UserRole.EMPLOYEE
    
    def can_view_all_checkins(self):
        return self.is_admin() or self.is_manager()
    
    def can_manage_users(self):
        return self.is_admin()
    
    def can_manage_locations(self):
        return self.is_admin() or self.is_manager()
    
    def get_display_name(self):
        return self.get_full_name() or self.username or self.email

class Location(models.Model):
    name = models.CharField(max_length=120)
    lat = models.FloatField()
    lng = models.FloatField()
    radius_m = models.PositiveIntegerField(default=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Checkin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    lat = models.FloatField()
    lng = models.FloatField()
    photo = models.ImageField(upload_to="checkins/%Y/%m/%d/")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    distance_m = models.FloatField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
