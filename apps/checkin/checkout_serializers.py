"""
Serializers for checkout module
"""

from rest_framework import serializers

from .models import Checkout
from .utils import get_location_name_for_checkin


class CheckoutSerializer(serializers.ModelSerializer):
    """Serializer for Checkout model"""

    user_name = serializers.CharField(source="user.get_display_name", read_only=True)
    checkin_id = serializers.IntegerField(source="checkin.id", read_only=True)
    checkin_location_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Checkout
        fields = [
            "id",
            "user",
            "user_name",
            "checkin",
            "checkin_id",
            "checkin_location_name",
            "location_name",
            "lat",
            "lng",
            "address",
            "photo",
            "photo_url",
            "note",
            "created_at",
            "distance_m",
            "ip",
            "user_agent",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "distance_m",
            "ip",
            "user_agent",
        ]

    def validate_lat(self, value):
        """Validate latitude"""
        if value < -90 or value > 90:
            msg = "Latitude must be between -90 and 90 degrees."
            raise serializers.ValidationError(msg)
        return value

    def validate_lng(self, value):
        """Validate longitude"""
        if value < -180 or value > 180:
            msg = "Longitude must be between -180 and 180 degrees."
            raise serializers.ValidationError(msg)
        return value

    def get_checkin_location_name(self, obj):
        """Get location name from related checkin"""
        return get_location_name_for_checkin(obj.checkin)

    def get_location_name(self, obj):
        """Get location name based on checkout lat/lng coordinates"""
        return get_location_name_for_checkin(obj)

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None


class CheckoutListSerializer(serializers.ModelSerializer):
    """Serializer for Checkout list view"""

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.get_display_name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    user_department_id = serializers.IntegerField(
        source="user.department_id", read_only=True
    )
    checkin_id = serializers.IntegerField(source="checkin.id", read_only=True)
    checkin_location_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Checkout
        fields = [
            "id",
            "user",
            "user_id",
            "employee_id",
            "user_name",
            "user_department_id",
            "checkin",
            "checkin_id",
            "checkin_location_name",
            "location_name",
            "lat",
            "lng",
            "address",
            "photo",
            "photo_url",
            "note",
            "created_at",
            "distance_m",
        ]
        read_only_fields = ["id", "user", "created_at", "distance_m"]

    def get_checkin_location_name(self, obj):
        """Get location name from related checkin"""
        return get_location_name_for_checkin(obj.checkin)

    def get_location_name(self, obj):
        """Get location name based on checkout lat/lng coordinates"""
        return get_location_name_for_checkin(obj)

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None
