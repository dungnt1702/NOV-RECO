"""
Forms for location module
"""

from django import forms

from .models import Location


class LocationForm(forms.ModelForm):
    """Form for creating and editing locations"""

    class Meta:
        model = Location
        fields = [
            "name",
            "description",
            "address",
            "lat",
            "lng",
            "radius_m",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "lat": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "lng": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "radius_m": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_lat(self):
        """Validate latitude"""
        lat = self.cleaned_data.get("lat")
        if lat is not None and (lat < -90 or lat > 90):
            raise forms.ValidationError("Latitude must be between -90 and 90 degrees.")
        return lat

    def clean_lng(self):
        """Validate longitude"""
        lng = self.cleaned_data.get("lng")
        if lng is not None and (lng < -180 or lng > 180):
            raise forms.ValidationError(
                "Longitude must be between -180 and 180 degrees."
            )
        return lng

    def clean_radius_m(self):
        """Validate radius"""
        radius = self.cleaned_data.get("radius_m")
        if radius is not None and radius <= 0:
            raise forms.ValidationError("Radius must be greater than 0 meters.")
        return radius
