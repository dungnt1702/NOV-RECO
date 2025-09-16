from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Location, Checkin, Area


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "department",
        "employee_id",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "department",
        "date_joined",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "employee_id",
        "phone",
    )
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "department",
                    "employee_id",
                )
            },
        ),
        (
            "Role & Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "lat",
        "lng",
        "radius_m",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("is_active", "created_by", "created_at")
    search_fields = ("name", "description", "created_by__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "description")}),
        ("Vị trí", {"fields": ("lat", "lng", "radius_m")}),
        ("Trạng thái", {"fields": ("is_active", "created_by")}),
        ("Thời gian", {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Nếu là tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "lat", "lng", "radius_m", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_location_name",
        "area",
        "location",
        "created_at",
        "distance_m",
        "note",
    )
    list_filter = ("area", "location", "created_at", "user__role")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "area__name",
        "location__name",
        "note",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "distance_m", "ip", "user_agent")

    fieldsets = (
        (None, {"fields": ("user", "area", "location")}),
        (
            "Check-in Details",
            {"fields": ("lat", "lng", "distance_m", "photo", "note")},
        ),
        ("System Info", {"fields": ("created_at", "ip", "user_agent")}),
    )

    def get_location_name(self, obj):
        return obj.get_location_name()

    get_location_name.short_description = "Vị trí"
