from django.conf import settings
from django.db import models


class CheckinType(models.TextChoices):
    WORK = '1', 'Chấm công'
    VISITOR = '2', 'Tiếp khách'


class Checkin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    area = models.ForeignKey(
        'area.Area', on_delete=models.CASCADE, null=True, blank=True
    )
    lat = models.FloatField()
    lng = models.FloatField()
    photo = models.ImageField(upload_to="checkins/%Y/%m/%d/")
    note = models.CharField(max_length=255, blank=True)
    checkin_type = models.CharField(
        max_length=1,
        choices=CheckinType.choices,
        default=CheckinType.WORK,
        help_text="Loại check-in"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    distance_m = models.FloatField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Check-in'
        verbose_name_plural = 'Check-ins'
        permissions = [
            # Checkin management permissions
            ("can_manage_checkins", "Can manage checkins"),
            ("can_view_checkins", "Can view checkins"),
            ("can_create_checkins", "Can create checkins"),
            ("can_edit_checkins", "Can edit checkins"),
            ("can_delete_checkins", "Can delete checkins"),
            ("can_view_all_checkins", "Can view all checkins"),
            ("can_view_own_checkins", "Can view own checkins"),
            
            # Checkin reports permissions
            ("can_view_checkin_reports", "Can view checkin reports"),
            ("can_export_checkin_data", "Can export checkin data"),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() if self.user else 'Unknown'} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def get_area_name(self):
        """Lấy tên khu vực"""
        if self.area:
            return self.area.name
        return "Khu vực không xác định"