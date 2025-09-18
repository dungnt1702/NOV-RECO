from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "department",
        "employee_id",
        "is_active",
    )
    list_filter = ("role", "is_active", "is_staff", "department")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "employee_id",
    )
    ordering = ("username",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Thông tin bổ sung",
            {"fields": ("role", "phone", "department", "employee_id")},
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Thông tin bổ sung",
            {"fields": ("role", "phone", "department", "employee_id")},
        ),
    )
