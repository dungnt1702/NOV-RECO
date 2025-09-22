from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, UserRole


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'date_joined']
    list_filter = ['role', 'department', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('role', 'department', 'phone', 'avatar', 'date_of_birth', 'gender', 'address')
        }),
        ('Thông tin khẩn cấp', {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Thông tin công việc', {
            'fields': ('position', 'hire_date', 'salary', 'work_schedule', 'skills', 'notes', 'is_active_employee'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'department', 'phone')
        }),
    )
