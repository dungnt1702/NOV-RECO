from rest_framework import serializers
from .models import Checkin, Location, User
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

class CheckinListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    created_at = serializers.DateTimeField(format='%d/%m/%Y %H:%M', read_only=True)
    
    class Meta:
        model = Checkin
        fields = ['id', 'user_name', 'user_email', 'location_name', 'lat', 'lng', 
                 'distance_m', 'note', 'created_at', 'photo']

class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'display_name', 
                 'role', 'phone', 'department', 'employee_id', 'is_active', 'date_joined']
