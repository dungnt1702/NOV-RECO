from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Area, Checkin
from .utils import haversine_m


@receiver(post_save, sender=Area)
def update_checkins_on_area_change(sender, instance, created, **kwargs):
    """Cập nhật check-in khi area được tạo mới hoặc cập nhật"""
    if not instance.is_active:
        return

    # Lấy tất cả check-in chưa có area hoặc có area khác
    checkins_to_update = Checkin.objects.filter(area__isnull=True).union(
        Checkin.objects.exclude(area=instance)
    )

    updated_count = 0

    for checkin in checkins_to_update:
        lat = checkin.lat
        lng = checkin.lng

        # Kiểm tra xem check-in có nằm trong area này không
        if instance.contains_point(lat, lng):
            # Tính khoảng cách
            distance = haversine_m(lat, lng, instance.lat, instance.lng)

            # Nếu check-in chưa có area hoặc area hiện tại xa hơn
            if not checkin.area or distance < checkin.distance_m:
                checkin.area = instance
                checkin.distance_m = distance
                checkin.save()
                updated_count += 1

    if updated_count > 0:
        print(
            f"Đã cập nhật {updated_count} check-in cho area '{instance.name}'"
        )


@receiver(post_delete, sender=Area)
def handle_area_deletion(sender, instance, **kwargs):
    """Xử lý khi area bị xóa"""
    # Cập nhật các check-in thuộc area này về area khác hoặc location
    affected_checkins = Checkin.objects.filter(area=instance)

    for checkin in affected_checkins:
        # Tìm area khác phù hợp
        areas = Area.objects.filter(is_active=True).exclude(id=instance.id)
        valid_areas = []

        for area in areas:
            if area.contains_point(checkin.lat, checkin.lng):
                dist = haversine_m(
                    checkin.lat, checkin.lng, area.lat, area.lng
                )
                valid_areas.append((area, dist))

        if valid_areas:
            # Chọn area gần nhất
            closest_area, closest_distance = min(
                valid_areas, key=lambda x: x[1]
            )
            checkin.area = closest_area
            checkin.distance_m = closest_distance
        else:
            # Fallback về location
            from .models import Location

            locations = Location.objects.filter(is_active=True)
            valid_locations = []

            for loc in locations:
                dist = haversine_m(checkin.lat, checkin.lng, loc.lat, loc.lng)
                if dist <= loc.radius_m:
                    valid_locations.append((loc, dist))

            if valid_locations:
                closest_location, closest_distance = min(
                    valid_locations, key=lambda x: x[1]
                )
                checkin.area = None
                checkin.location = closest_location
                checkin.distance_m = closest_distance
            else:
                # Không tìm thấy area/location phù hợp
                checkin.area = None
                checkin.location = None
                checkin.distance_m = None

        checkin.save()

    print(
        f"Đã xử lý {affected_checkins.count()} check-in sau khi xóa area '{instance.name}'"
    )
