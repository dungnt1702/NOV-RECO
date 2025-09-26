from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Checkin
from apps.location.models import Location
from .utils import haversine_distance


@receiver(post_save, sender=Checkin)
def update_checkin_distance(sender, instance, created, **kwargs):
    """Cập nhật khoảng cách khi tạo check-in"""
    if created and instance.location:
        distance = haversine_distance(
            instance.location.lat, 
            instance.location.lng, 
            instance.lat, 
            instance.lng
        )
        instance.distance_m = distance
        instance.save(update_fields=['distance_m'])


@receiver(post_save, sender=Location)
def update_checkins_for_location(sender, instance, created, **kwargs):
    """Cập nhật khoảng cách cho tất cả check-ins trong địa điểm khi địa điểm thay đổi"""
    if not created:  # Chỉ cập nhật khi địa điểm được sửa đổi
        checkins = Checkin.objects.filter(location=instance)
        for checkin in checkins:
            distance = haversine_distance(
                instance.lat, 
                instance.lng, 
                checkin.lat, 
                checkin.lng
            )
            checkin.distance_m = distance
            checkin.save(update_fields=['distance_m'])