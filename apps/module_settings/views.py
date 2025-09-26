from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import ModuleSettings


def is_superuser(user):
    """Kiểm tra user có phải Super admin không"""
    return user.is_superuser


@user_passes_test(is_superuser)
@staff_member_required
def module_settings_list(request):
    """Danh sách tất cả module settings"""
    modules = ModuleSettings.objects.all().order_by('module_name')
    
    # Tính toán statistics
    total_count = modules.count()
    enabled_count = modules.filter(is_enabled=True).count()
    disabled_count = modules.filter(is_enabled=False).count()
    enabled_percentage = round((enabled_count / total_count * 100) if total_count > 0 else 0, 1)
    
    context = {
        'modules': modules,
        'total_count': total_count,
        'enabled_count': enabled_count,
        'disabled_count': disabled_count,
        'enabled_percentage': enabled_percentage,
        'title': 'Quản lý Modules',
    }
    
    return render(request, 'admin/module_settings/list.html', context)


@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def toggle_module(request, module_name):
    """Bật/tắt module"""
    try:
        module = get_object_or_404(ModuleSettings, module_name=module_name)
        module.is_enabled = not module.is_enabled
        module.save()
        
        status = "bật" if module.is_enabled else "tắt"
        messages.success(
            request, 
            f'Đã {status} module "{module.display_name}" thành công!'
        )
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'is_enabled': module.is_enabled,
                'message': f'Module "{module.display_name}" đã được {status}'
            })
        
        return redirect('module_settings:list')
        
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, f'Lỗi: {str(e)}')
        return redirect('module_settings:list')


@user_passes_test(is_superuser)
def module_status_api(request):
    """API để lấy trạng thái tất cả modules"""
    modules = ModuleSettings.objects.all()
    
    data = {
        'modules': [
            {
                'module_name': module.module_name,
                'display_name': module.display_name,
                'is_enabled': module.is_enabled,
                'description': module.description,
            }
            for module in modules
        ]
    }
    
    return JsonResponse(data)
