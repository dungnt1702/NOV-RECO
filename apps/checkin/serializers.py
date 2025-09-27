"""
Serializers for checkin module
"""

from rest_framework import serializers

from .checkout_serializers import CheckoutListSerializer, CheckoutSerializer
from .models import Checkin, Checkout
from .utils import get_location_name_for_checkin, find_best_location_for_checkin


class CheckinSerializer(serializers.ModelSerializer):
    """Serializer for Checkin model"""

    user_name = serializers.CharField(source="user.get_display_name", read_only=True)
    location_name = serializers.SerializerMethodField()
    checkin_type_display = serializers.CharField(
        source="get_checkin_type_display", read_only=True
    )
    photo_url = serializers.SerializerMethodField()
    has_checkout = serializers.SerializerMethodField()

    class Meta:
        model = Checkin
        fields = [
            "id",
            "user",
            "user_name",
            "location",
            "location_name",
            "lat",
            "lng",
            "address",
            "photo",
            "photo_url",
            "note",
            "checkin_type",
            "checkin_type_display",
            "created_at",
            "distance_m",
            "ip",
            "user_agent",
            "has_checkout",
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

    def get_location_name(self, obj):
        """Get location name based on lat/lng coordinates"""
        return get_location_name_for_checkin(obj)
    
    def get_distance_m(self, obj):
        """Get distance dynamically based on current locations"""
        if obj.distance_m is not None:
            return obj.distance_m
        
        # Calculate distance dynamically if not stored
        location_name, distance = find_best_location_for_checkin(obj.lat, obj.lng)
        return distance

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None

    def get_has_checkout(self, obj):
        """Check if this checkin has a checkout"""
        return obj.checkouts.exists()


class CheckinListSerializer(serializers.ModelSerializer):
    """Serializer for Checkin list view"""

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.get_display_name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    user_department_id = serializers.IntegerField(
        source="user.department_id", read_only=True
    )
    location_id = serializers.IntegerField(source="location.id", read_only=True)
    location_name = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()
    checkin_type_display = serializers.CharField(
        source="get_checkin_type_display", read_only=True
    )
    photo_url = serializers.SerializerMethodField()
    has_checkout = serializers.SerializerMethodField()

    class Meta:
        model = Checkin
        fields = [
            "id",
            "user",
            "user_id",
            "employee_id",
            "user_name",
            "user_department_id",
            "location",
            "location_id",
            "location_name",
            "lat",
            "lng",
            "address",
            "photo",
            "photo_url",
            "note",
            "checkin_type",
            "checkin_type_display",
            "created_at",
            "distance_m",
            "has_checkout",
        ]
        read_only_fields = ["id", "user", "created_at", "distance_m"]

    def get_location_name(self, obj):
        """Get location name based on lat/lng coordinates"""
        return get_location_name_for_checkin(obj)
    
    def get_distance_m(self, obj):
        """Get distance dynamically based on current locations"""
        if obj.distance_m is not None:
            return obj.distance_m
        
        # Calculate distance dynamically if not stored
        location_name, distance = find_best_location_for_checkin(obj.lat, obj.lng)
        return distance

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None

    def get_has_checkout(self, obj):
        """Check if this checkin has a checkout"""
        return obj.checkouts.exists()
