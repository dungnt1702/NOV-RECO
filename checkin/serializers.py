from rest_framework import serializers
from .models import Checkin, Location, User
from .utils import haversine_m


class CheckinCreateSerializer(serializers.ModelSerializer):
    checkin_time = serializers.DateTimeField(required=False)

    class Meta:
        model = Checkin
        fields = ["lat", "lng", "photo", "note", "checkin_time"]

    def validate(self, data):
        # Tìm địa điểm gần nhất trong bán kính cho phép
        lat = data["lat"]
        lng = data["lng"]

        # Lấy tất cả địa điểm active
        locations = Location.objects.filter(is_active=True)
        valid_locations = []

        for loc in locations:
            dist = haversine_m(lat, lng, loc.lat, loc.lng)
            if dist <= loc.radius_m:
                valid_locations.append((loc, dist))

        if not valid_locations:
            # Tạo địa điểm mặc định nếu không có
            default_location, created = Location.objects.get_or_create(
                name="Vị trí tự do",
                defaults={
                    "lat": lat,
                    "lng": lng,
                    "radius_m": 1000,  # Bán kính 1km
                    "is_active": True,
                },
            )
            data["_location"] = default_location
            data["_distance_m"] = 0
        else:
            # Chọn địa điểm gần nhất
            closest_location, closest_distance = min(
                valid_locations, key=lambda x: x[1]
            )
            data["_location"] = closest_location
            data["_distance_m"] = closest_distance

        return data

    def create(self, validated):
        req = self.context["request"]
        user = req.user
        loc = validated.pop("_location")
        dist = validated.pop("_distance_m")

        # Sử dụng checkin_time nếu có
        checkin_time = validated.pop("checkin_time", None)

        return Checkin.objects.create(
            user=user,
            location=loc,
            distance_m=dist,
            ip=req.META.get("REMOTE_ADDR"),
            user_agent=req.META.get("HTTP_USER_AGENT", "")[:255],
            created_at=checkin_time,
            **validated
        )


class CheckinListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.get_display_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    class Meta:
        model = Checkin
        fields = [
            "id",
            "user_id",
            "user_name",
            "user_email",
            "location_name",
            "lat",
            "lng",
            "distance_m",
            "note",
            "created_at",
            "photo",
        ]


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="get_display_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "role",
            "phone",
            "department",
            "employee_id",
            "is_active",
            "date_joined",
        ]
