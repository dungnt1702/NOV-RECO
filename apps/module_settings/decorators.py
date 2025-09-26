from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from .models import ModuleSettings


def require_module_enabled(module_name):
    """
    Decorator để kiểm tra module có được bật hay không
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not ModuleSettings.is_module_enabled(module_name):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'error': 'Module này đã bị tắt',
                        'module': module_name
                    }, status=403)
                
                # Render trang thông báo module bị tắt
                context = {
                    'module_name': module_name,
                    'title': 'Module không khả dụng'
                }
                return render(request, 'module_settings/disabled.html', context, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def module_enabled_context_processor(request):
    """
    Context processor để thêm thông tin về modules vào tất cả templates
    """
    enabled_modules = list(ModuleSettings.get_enabled_modules())
    disabled_modules = list(ModuleSettings.get_disabled_modules())
    
    return {
        'enabled_modules': enabled_modules,
        'disabled_modules': disabled_modules,
        'is_module_enabled': ModuleSettings.is_module_enabled,
    }
