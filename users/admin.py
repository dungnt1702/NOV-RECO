from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'employee_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description')
        }),
        ('Quản lý', {
            'fields': ('manager',)
        }),
    )
    
    def employee_count(self, obj):
        return obj.employee_count
    employee_count.short_description = 'Số nhân viên'


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
