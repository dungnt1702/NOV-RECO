"""
Serializers for location module
"""

from rest_framework import serializers

from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "description",
            "address",
            "lat",
            "lng",
            "radius_m",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_lat(self, value):
        """Validate latitude"""
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90 degrees."
            )
        return value

    def validate_lng(self, value):
        """Validate longitude"""
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180 degrees."
            )
        return value

    def validate_radius_m(self, value):
        """Validate radius"""
        if value <= 0:
            raise serializers.ValidationError("Radius must be greater than 0 meters.")
        return value
