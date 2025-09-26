from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import resolve
from .models import ModuleSettings


class ModulePermissionMiddleware(MiddlewareMixin):
    """
    Middleware để kiểm tra quyền truy cập module
    """
    
    # Mapping URL patterns to module names
    MODULE_URL_MAPPING = {
        'checkin:': 'checkin',
        'location:': 'location',
        'users:': 'users',
        'dashboard:': 'dashboard',
        'notifications:': 'notifications',
        'absence:': 'absence',
        'automation_test:': 'automation_test',
    }
    
    def process_request(self, request):
        """Kiểm tra quyền truy cập module trước khi xử lý request"""
        
        # Chỉ kiểm tra với authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Super admin có thể truy cập tất cả
        if request.user.is_superuser:
            return None
        
        # Lấy URL name hiện tại
        try:
            resolver_match = resolve(request.path)
            url_name = resolver_match.url_name
            namespace = resolver_match.namespace
        except:
            return None
        
        # Tạo full URL name
        full_url_name = f"{namespace}:{url_name}" if namespace else url_name
        
        # Kiểm tra từng module
        for url_prefix, module_name in self.MODULE_URL_MAPPING.items():
            if full_url_name.startswith(url_prefix):
                if not ModuleSettings.is_module_enabled(module_name):
                    # Module bị tắt, từ chối truy cập
                    if request.headers.get('Accept') == 'application/json':
                        return HttpResponseForbidden(
                            '{"error": "Module này đã bị tắt"}',
                            content_type='application/json'
                        )
                    
                    # Render trang thông báo
                    context = {
                        'module_name': module_name,
                        'title': 'Module không khả dụng'
                    }
                    return render(request, 'module_settings/disabled.html', context, status=403)
                break
        
        return None
