from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ModuleSettings(models.Model):
    """Model để quản lý trạng thái bật/tắt của các modules"""
    
    MODULE_CHOICES = [
        ('checkin', 'Check-in System'),
        ('location', 'Location Management'),
        ('users', 'User Management'),
        ('dashboard', 'Dashboard'),
        ('notifications', 'Notifications'),
        ('absence', 'Absence Management'),
        ('reports', 'Reports'),
        ('analytics', 'Analytics'),
        ('automation_test', 'Automation Testing'),
    ]
    
    module_name = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        unique=True,
        help_text="Tên module"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Module có được bật hay không"
    )
    
    display_name = models.CharField(
        max_length=100,
        help_text="Tên hiển thị của module"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Mô tả chức năng của module"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Người tạo setting"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Module Setting"
        verbose_name_plural = "Module Settings"
        ordering = ['module_name']
    
    def __str__(self):
        status = "Bật" if self.is_enabled else "Tắt"
        return f"{self.display_name} ({self.module_name}) - {status}"
    
    @classmethod
    def is_module_enabled(cls, module_name):
        """Kiểm tra xem module có được bật hay không"""
        try:
            setting = cls.objects.get(module_name=module_name)
            return setting.is_enabled
        except cls.DoesNotExist:
            # Nếu không có setting, mặc định là bật
            return True
    
    @classmethod
    def get_enabled_modules(cls):
        """Lấy danh sách các modules được bật"""
        return cls.objects.filter(is_enabled=True).values_list('module_name', flat=True)
    
    @classmethod
    def get_disabled_modules(cls):
        """Lấy danh sách các modules bị tắt"""
        return cls.objects.filter(is_enabled=False).values_list('module_name', flat=True)
