"""
Serializers for checkin module
"""

from rest_framework import serializers
from .models import Checkin


class CheckinSerializer(serializers.ModelSerializer):
    """Serializer for Checkin model"""
    
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    
    class Meta:
        model = Checkin
        fields = [
            'id', 'user', 'user_name', 'area', 'area_name', 'lat', 'lng', 
            'photo', 'note', 'created_at', 'distance_m', 'ip', 'user_agent'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'distance_m', 'ip', 'user_agent']
        
    def validate_lat(self, value):
        """Validate latitude"""
        if value < -90 or value > 90:
            raise serializers.ValidationError('Latitude must be between -90 and 90 degrees.')
        return value
        
    def validate_lng(self, value):
        """Validate longitude"""
        if value < -180 or value > 180:
            raise serializers.ValidationError('Longitude must be between -180 and 180 degrees.')
        return value


class CheckinListSerializer(serializers.ModelSerializer):
    """Serializer for Checkin list view"""
    
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    
    class Meta:
        model = Checkin
        fields = [
            'id', 'user', 'user_name', 'area', 'area_name', 'lat', 'lng', 
            'photo', 'note', 'created_at', 'distance_m'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'distance_m']