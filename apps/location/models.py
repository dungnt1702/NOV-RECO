from django.conf import settings
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=120, help_text="Tên địa điểm")
    description = models.TextField(blank=True, help_text="Mô tả địa điểm")
    address = models.TextField(blank=True, help_text="Địa chỉ chi tiết")
    lat = models.FloatField(help_text="Vĩ độ trung tâm")
    lng = models.FloatField(help_text="Kinh độ trung tâm")
    radius_m = models.PositiveIntegerField(default=100, help_text="Bán kính (mét)")
    is_active = models.BooleanField(default=True, help_text="Địa điểm có hoạt động")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Người tạo địa điểm",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Địa điểm"
        verbose_name_plural = "Địa điểm"
        permissions = [
            # Location management permissions
            ("can_manage_locations", "Can manage locations"),
            ("can_view_locations", "Can view locations"),
            ("can_create_locations", "Can create locations"),
            ("can_edit_locations", "Can edit locations"),
            ("can_delete_locations", "Can delete locations"),
            ("can_activate_locations", "Can activate/deactivate locations"),
        ]

    def __str__(self):
        return f"{self.name} ({self.radius_m}m)"

    def contains_point(self, lat, lng):
        """Kiểm tra xem một điểm có nằm trong địa điểm không"""
        from apps.checkin.utils import haversine_m

        distance = haversine_m(self.lat, self.lng, lat, lng)
        return distance <= self.radius_m
