from rest_framework import serializers
from .models import Checkin, Area
from users.models import User
from .utils import haversine_m


class CheckinCreateSerializer(serializers.ModelSerializer):
    checkin_time = serializers.DateTimeField(required=False)

    class Meta:
        model = Checkin
        fields = ["lat", "lng", "photo", "note", "checkin_time"]

    def validate(self, data):
        # Tìm khu vực gần nhất trong bán kính cho phép
        lat = data["lat"]
        lng = data["lng"]

        # Tìm trong Area
        areas = Area.objects.filter(is_active=True)
        valid_areas = []

        for area in areas:
            if area.contains_point(lat, lng):
                dist = haversine_m(lat, lng, area.lat, area.lng)
                valid_areas.append((area, dist))

        if valid_areas:
            # Chọn khu vực gần nhất
            closest_area, closest_distance = min(
                valid_areas, key=lambda x: x[1]
            )
            data["_area"] = closest_area
            data["_distance_m"] = closest_distance
        else:
            # Tạo khu vực mặc định nếu không có
            default_area, created = Area.objects.get_or_create(
                name="Khu vực tự do",
                defaults={
                    "lat": lat,
                    "lng": lng,
                    "radius_m": 1000,  # Bán kính 1km
                    "is_active": True,
                    "description": "Khu vực mặc định cho check-in tự do",
                },
            )
            data["_area"] = default_area
            data["_distance_m"] = 0

        return data

    def create(self, validated):
        req = self.context["request"]
        user = req.user
        area = validated.pop("_area", None)
        dist = validated.pop("_distance_m")

        # Sử dụng checkin_time nếu có, nếu không thì dùng thời gian hiện tại
        checkin_time = validated.pop("checkin_time", None)
        if checkin_time is None:
            from django.utils import timezone

            checkin_time = timezone.now()

        return Checkin.objects.create(
            user=user,
            area=area,
            distance_m=dist,
            ip=req.META.get("REMOTE_ADDR"),
            user_agent=req.META.get("HTTP_USER_AGENT", "")[:255],
            created_at=checkin_time,
            **validated,
        )


class CheckinListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(
        source="user.get_display_name", read_only=True
    )
    user_email = serializers.CharField(source="user.email", read_only=True)
    area_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    class Meta:
        model = Checkin
        fields = [
            "id",
            "user_id",
            "user_name",
            "user_email",
            "area_name",
            "area",
            "lat",
            "lng",
            "distance_m",
            "note",
            "created_at",
            "photo",
        ]

    def get_area_name(self, obj):
        return obj.get_area_name()


class AreaSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_display_name", read_only=True
    )
    created_at = serializers.DateTimeField(
        format="%d/%m/%Y %H:%M", read_only=True
    )

    class Meta:
        model = Area
        fields = [
            "id",
            "name",
            "description",
            "lat",
            "lng",
            "radius_m",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(
        source="get_display_name", read_only=True
    )
    role_display = serializers.CharField(
        source="get_role_display", read_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "role",
            "role_display",
            "phone",
            "department",
            "employee_id",
            "is_active",
            "date_joined",
        ]
