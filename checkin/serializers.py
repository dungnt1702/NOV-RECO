from rest_framework import serializers
from .models import Checkin, Location
from .utils import haversine_m

class CheckinCreateSerializer(serializers.ModelSerializer):
    location_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Checkin
        fields = ["location_id", "lat", "lng", "photo", "note"]

    def validate(self, data):
        try:
            loc = Location.objects.get(id=data["location_id"], is_active=True)
        except Location.DoesNotExist:
            raise serializers.ValidationError("Địa điểm không hợp lệ hoặc đã tạm khóa.")
        dist = haversine_m(data["lat"], data["lng"], loc.lat, loc.lng)
        if dist > loc.radius_m:
            raise serializers.ValidationError(f"Bạn đang ở ngoài bán kính check-in ({int(dist)}m > {loc.radius_m}m).")
        data["_location"] = loc
        data["_distance_m"] = dist
        return data

    def create(self, validated):
        req = self.context["request"]
        user = req.user
        loc = validated.pop("_location")
        dist = validated.pop("_distance_m")
        return Checkin.objects.create(
            user=user,
            location=loc,
            distance_m=dist,
            ip = req.META.get("REMOTE_ADDR"),
            user_agent = req.META.get("HTTP_USER_AGENT", "")[:255],
            **validated
        )
