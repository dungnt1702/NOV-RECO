"""
Forms for checkin module
"""

from django import forms

from .models import Checkin


class CheckinForm(forms.ModelForm):
    """Form for creating check-ins"""

    class Meta:
        model = Checkin
        fields = ["area", "lat", "lng", "note", "photo"]
        widgets = {
            "area": forms.Select(attrs={"class": "form-control"}),
            "lat": forms.NumberInput(
                attrs={"class": "form-control", "step": "any", "readonly": True}
            ),
            "lng": forms.NumberInput(
                attrs={"class": "form-control", "step": "any", "readonly": True}
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Ghi chú (tùy chọn)",
                }
            ),
            "photo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
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
