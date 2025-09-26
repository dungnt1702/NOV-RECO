from django.contrib import admin
from .models import ModuleSettings


@admin.register(ModuleSettings)
class ModuleSettingsAdmin(admin.ModelAdmin):
    """Admin interface cho ModuleSettings - chỉ Super admin mới có quyền"""
    
    list_display = [
        'module_name', 'display_name', 'is_enabled', 
        'description', 'created_at', 'updated_at'
    ]
    
    list_filter = ['is_enabled', 'module_name', 'created_at']
    
    search_fields = ['module_name', 'display_name', 'description']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin Module', {
            'fields': ('module_name', 'display_name', 'description')
        }),
        ('Trạng thái', {
            'fields': ('is_enabled',)
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Chỉ Super admin mới có thể thêm"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Chỉ Super admin mới có thể sửa"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Chỉ Super admin mới có thể xóa"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Chỉ Super admin mới có thể xem"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        """Tự động gán created_by khi tạo mới"""
        if not change:  # Nếu là tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Chỉ Super admin mới thấy được"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        return ModuleSettings.objects.none()
    
    actions = ['enable_modules', 'disable_modules']
    
    def enable_modules(self, request, queryset):
        """Action để bật các modules được chọn"""
        updated = queryset.update(is_enabled=True)
        self.message_user(
            request,
            f'Đã bật {updated} module(s).'
        )
    enable_modules.short_description = "Bật các modules được chọn"
    
    def disable_modules(self, request, queryset):
        """Action để tắt các modules được chọn"""
        updated = queryset.update(is_enabled=False)
        self.message_user(
            request,
            f'Đã tắt {updated} module(s).'
        )
    disable_modules.short_description = "Tắt các modules được chọn"
