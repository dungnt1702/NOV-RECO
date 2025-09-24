from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """Thông báo hệ thống"""
    NOTIFICATION_TYPES = [
        ('approval_required', 'Cần phê duyệt'),
        ('approval_completed', 'Đã phê duyệt'),
        ('approval_rejected', 'Bị từ chối'),
        ('reminder', 'Nhắc nhở'),
        ('system', 'Hệ thống'),
        ('checkin', 'Chấm công'),
        ('absence', 'Vắng mặt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Người nhận")
    title = models.CharField(max_length=200, help_text="Tiêu đề")
    message = models.TextField(help_text="Nội dung")
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, help_text="Loại thông báo")
    is_read = models.BooleanField(default=False, help_text="Đã đọc")
    is_important = models.BooleanField(default=False, help_text="Quan trọng")
    
    # Dữ liệu liên quan
    data = models.JSONField(default=dict, blank=True, help_text="Dữ liệu bổ sung")
    related_object_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID đối tượng liên quan")
    related_object_type = models.CharField(max_length=100, blank=True, help_text="Loại đối tượng liên quan")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian đọc")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian hết hạn")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    @property
    def type_display(self):
        """Hiển thị loại thông báo"""
        type_map = {
            'approval_required': 'Cần phê duyệt',
            'approval_completed': 'Đã phê duyệt',
            'approval_rejected': 'Bị từ chối',
            'reminder': 'Nhắc nhở',
            'system': 'Hệ thống',
            'checkin': 'Chấm công',
            'absence': 'Vắng mặt',
        }
        return type_map.get(self.type, self.type)
    
    @property
    def is_expired(self):
        """Kiểm tra thông báo có hết hạn không"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_read(self):
        """Đánh dấu đã đọc"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def get_unread_count(cls, user):
        """Lấy số thông báo chưa đọc của user"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def get_unread_notifications(cls, user, limit=10):
        """Lấy danh sách thông báo chưa đọc"""
        return cls.objects.filter(
            user=user, 
            is_read=False
        ).order_by('-created_at')[:limit]