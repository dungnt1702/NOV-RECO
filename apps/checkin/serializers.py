from rest_framework import serializers
from .models import Checkin
from apps.area.models import Area
from apps.users.models import User


class AreaSerializer(serializers.ModelSerializer):
    """Serializer cho Area"""
    class Meta:
        model = Area
        fields = ['id', 'name', 'description', 'lat', 'lng', 'radius_m', 'is_active']


class CheckinListSerializer(serializers.ModelSerializer):
    """Serializer cho danh sách Checkin"""
    user_name = serializers.SerializerMethodField()
    area_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Checkin
        fields = [
            'id', 'user_name', 'area_name', 'lat', 'lng', 'photo', 'note',
            'created_at', 'distance_m'
        ]
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'Unknown'
    
    def get_area_name(self, obj):
        return obj.get_area_name()


class CheckinCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo Checkin"""
    class Meta:
        model = Checkin
        fields = ['area', 'lat', 'lng', 'photo', 'note']
    
    def create(self, validated_data):
        # Thêm user từ request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)