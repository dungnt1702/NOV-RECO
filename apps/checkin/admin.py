from django.contrib import admin
from .models import Checkin


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    list_display = ['user', 'area', 'created_at', 'distance_m', 'note']
    list_filter = ['created_at', 'area', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'note']
    readonly_fields = ['created_at', 'distance_m', 'ip', 'user_agent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'area', 'lat', 'lng', 'photo', 'note')
        }),
        ('Thông tin kỹ thuật', {
            'fields': ('distance_m', 'ip', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
