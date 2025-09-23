"""
Serializers for checkin module
"""

from rest_framework import serializers
from .models import Checkin


class CheckinSerializer(serializers.ModelSerializer):
    """Serializer for Checkin model"""
    
    user_name = serializers.CharField(
        source='user.get_display_name', read_only=True
    )
    area_name = serializers.CharField(
        source='area.name', read_only=True
    )
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Checkin
        fields = [
            'id', 'user', 'user_name', 'area', 'area_name', 'lat', 'lng',
            'photo', 'photo_url', 'note', 'created_at', 'distance_m',
            'ip', 'user_agent'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'distance_m', 'ip', 'user_agent'
        ]

    def validate_lat(self, value):
        """Validate latitude"""
        if value < -90 or value > 90:
            msg = (
                'Latitude must be between -90 and 90 degrees.'
            )
            raise serializers.ValidationError(msg)
        return value

    def validate_lng(self, value):
        """Validate longitude"""
        if value < -180 or value > 180:
            msg = (
                'Longitude must be between -180 and 180 degrees.'
            )
            raise serializers.ValidationError(msg)
        return value

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None


class CheckinListSerializer(serializers.ModelSerializer):
    """Serializer for Checkin list view"""
    
    user_name = serializers.CharField(
        source='user.get_display_name', read_only=True
    )
    area_name = serializers.CharField(
        source='area.name', read_only=True
    )
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Checkin
        fields = [
            'id', 'user', 'user_name', 'area', 'area_name', 'lat', 'lng',
            'photo', 'photo_url', 'note', 'created_at', 'distance_m'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'distance_m']

    def get_photo_url(self, obj):
        try:
            if obj.photo:
                return obj.photo.url
        except Exception:
            pass
        return None
