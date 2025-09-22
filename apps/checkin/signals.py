from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Checkin
from apps.area.models import Area
from .utils import haversine_m


@receiver(post_save, sender=Checkin)
def update_checkin_distance(sender, instance, created, **kwargs):
    """Cập nhật khoảng cách khi tạo check-in"""
    if created and instance.area:
        distance = haversine_m(
            instance.area.lat, 
            instance.area.lng, 
            instance.lat, 
            instance.lng
        )
        instance.distance_m = distance
        instance.save(update_fields=['distance_m'])


@receiver(post_save, sender=Area)
def update_checkins_for_area(sender, instance, created, **kwargs):
    """Cập nhật khoảng cách cho tất cả check-ins trong khu vực khi khu vực thay đổi"""
    if not created:  # Chỉ cập nhật khi khu vực được sửa đổi
        checkins = Checkin.objects.filter(area=instance)
        for checkin in checkins:
            distance = haversine_m(
                instance.lat, 
                instance.lng, 
                checkin.lat, 
                checkin.lng
            )
            checkin.distance_m = distance
            checkin.save(update_fields=['distance_m'])