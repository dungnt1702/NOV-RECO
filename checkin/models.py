from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


# User Roles
class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Quản lý"
    EMPLOYEE = "employee", "Nhân viên"


# Custom User Model
class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        help_text="Vai trò của người dùng trong hệ thống",
    )
    phone = models.CharField(
        max_length=15, blank=True, help_text="Số điện thoại"
    )
    department = models.CharField(
        max_length=100, blank=True, help_text="Phòng ban"
    )
    employee_id = models.CharField(
        max_length=20, blank=True, unique=True, help_text="Mã nhân viên"
    )

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


class Area(models.Model):
    name = models.CharField(max_length=120, help_text="Tên khu vực")
    description = models.TextField(blank=True, help_text="Mô tả khu vực")
    lat = models.FloatField(help_text="Vĩ độ trung tâm")
    lng = models.FloatField(help_text="Kinh độ trung tâm")
    radius_m = models.PositiveIntegerField(
        default=100, help_text="Bán kính (mét)"
    )
    is_active = models.BooleanField(
        default=True, help_text="Khu vực có hoạt động"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Người tạo khu vực",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Khu vực"
        verbose_name_plural = "Khu vực"

    def __str__(self):
        return f"{self.name} ({self.radius_m}m)"

    def contains_point(self, lat, lng):
        """Kiểm tra xem một điểm có nằm trong khu vực không"""
        from .utils import haversine_m

        distance = haversine_m(self.lat, self.lng, lat, lng)
        return distance <= self.radius_m


class Location(models.Model):
    name = models.CharField(max_length=120)
    lat = models.FloatField()
    lng = models.FloatField()
    radius_m = models.PositiveIntegerField(default=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Checkin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE, null=True, blank=True
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, blank=True
    )
    lat = models.FloatField()
    lng = models.FloatField()
    photo = models.ImageField(upload_to="checkins/%Y/%m/%d/")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    distance_m = models.FloatField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    def get_location_name(self):
        """Lấy tên vị trí từ area hoặc location"""
        if self.area:
            return self.area.name
        elif self.location:
            return self.location.name
        return "Vị trí không xác định"
