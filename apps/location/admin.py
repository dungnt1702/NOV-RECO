from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "address",
        "lat",
        "lng",
        "radius_m",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description", "address"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Thông tin cơ bản",
            {"fields": ("name", "description", "address", "is_active")},
        ),
        ("Vị trí", {"fields": ("lat", "lng", "radius_m")}),
        (
            "Thông tin hệ thống",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
