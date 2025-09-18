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
        return self.role == UserRole.ADMIN or self.is_superuser

    def is_manager(self):
        return self.role == UserRole.MANAGER

    def is_employee(self):
        return self.role == UserRole.EMPLOYEE
    
    # Properties for template usage
    @property
    def is_admin_user(self):
        return self.is_admin()
    
    @property
    def is_manager_user(self):
        return self.is_manager()
    
    @property
    def is_employee_user(self):
        return self.is_employee()

    def can_view_all_checkins(self):
        return self.is_superuser or self.is_admin() or self.is_manager()

    def can_manage_users(self):
        return self.is_superuser or self.is_admin()

    def can_manage_locations(self):
        return self.is_superuser or self.is_admin() or self.is_manager()

    def get_display_name(self):
        return self.get_full_name() or self.username or self.email

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
