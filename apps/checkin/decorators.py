from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apps.users.models import UserRole


def role_required(allowed_roles):
    """
    Decorator để kiểm tra quyền truy cập dựa trên role
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            # Cho phép superuser truy cập tất cả
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not hasattr(request.user, 'role'):
                messages.error(request, 'Tài khoản không có quyền truy cập.')
                return redirect('dashboard:personal')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('dashboard:personal')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator cho admin"""
    return role_required([UserRole.ADMIN])(view_func)


def manager_required(view_func):
    """Decorator cho manager"""
    return role_required([UserRole.ADMIN, UserRole.MANAGER])(view_func)


def hcns_required(view_func):
    """Decorator cho HCNS"""
    return role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])(view_func)


def employee_required(view_func):
    """Decorator cho employee"""
    return role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS, UserRole.EMPLOYEE])(view_func)


def user_management_required(view_func):
    """Decorator cho user management"""
    return role_required([UserRole.ADMIN, UserRole.MANAGER])(view_func)
