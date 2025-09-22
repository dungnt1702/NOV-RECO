from django.contrib import admin
from .models import Area


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'lat', 'lng', 'radius_m', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Vị trí', {
            'fields': ('lat', 'lng', 'radius_m')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
