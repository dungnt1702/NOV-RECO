from django.conf import settings
from django.db import models

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
