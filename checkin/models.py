from django.conf import settings
from django.db import models


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
        null=True,
        blank=True,
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


class Checkin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE, null=True, blank=True
    )
    lat = models.FloatField()
    lng = models.FloatField()
    photo = models.ImageField(upload_to="checkins/%Y/%m/%d/")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    distance_m = models.FloatField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    def get_area_name(self):
        """Lấy tên khu vực"""
        if self.area:
            return self.area.name
        return "Khu vực không xác định"
