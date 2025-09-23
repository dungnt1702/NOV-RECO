from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def permission_required(permission_name):
    """
    Decorator để kiểm tra quyền truy cập dựa trên Django permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            # Superuser có tất cả quyền
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Kiểm tra permission
            if not request.user.has_perm(permission_name):
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('dashboard:personal')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def group_required(group_names):
    """
    Decorator để kiểm tra user có thuộc group nào đó không
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            # Superuser có tất cả quyền
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Kiểm tra group
            if isinstance(group_names, str):
                group_list = [group_names]
            else:
                group_list = group_names
                
            if not request.user.groups.filter(name__in=group_list).exists():
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('dashboard:personal')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Specific decorators for common permissions
def super_admin_required(view_func):
    """Chỉ Super Admin"""
    return group_required('Super Admin')(view_func)


def admin_required(view_func):
    """Admin và Super Admin"""
    return group_required(['Admin', 'Super Admin'])(view_func)


def manager_required(view_func):
    """Manager, Admin và Super Admin"""
    return group_required(['Manager', 'Admin', 'Super Admin'])(view_func)


def hr_required(view_func):
    """HR, Manager, Admin và Super Admin"""
    return group_required(['HR', 'Manager', 'Admin', 'Super Admin'])(view_func)


def secretary_required(view_func):
    """Secretary, Manager, Admin và Super Admin"""
    return group_required(['Secretary', 'Manager', 'Admin', 'Super Admin'])(view_func)


def employee_required(view_func):
    """Tất cả users"""
    return group_required(['Employee', 'Secretary', 'HR', 'Manager', 'Admin', 'Super Admin'])(view_func)


# Permission-based decorators
def can_manage_users(view_func):
    """Có quyền quản lý users"""
    return permission_required('users.can_manage_users')(view_func)


def can_view_users(view_func):
    """Có quyền xem users"""
    return permission_required('users.can_view_users')(view_func)


def can_manage_checkins(view_func):
    """Có quyền quản lý checkins"""
    return permission_required('checkin.can_manage_checkins')(view_func)


def can_view_all_checkins(view_func):
    """Có quyền xem tất cả checkins"""
    return permission_required('checkin.can_view_all_checkins')(view_func)


def can_manage_areas(view_func):
    """Có quyền quản lý areas"""
    return permission_required('area.can_manage_areas')(view_func)


def can_view_areas(view_func):
    """Có quyền xem areas"""
    return permission_required('area.can_view_areas')(view_func)


def can_manage_departments(view_func):
    """Có quyền quản lý departments"""
    return permission_required('users.can_manage_departments')(view_func)


def can_view_checkin_reports(view_func):
    """Có quyền xem báo cáo checkin"""
    return permission_required('checkin.can_view_checkin_reports')(view_func)


def can_create_checkins(view_func):
    """Có quyền tạo checkins"""
    return permission_required('checkin.can_create_checkins')(view_func)


def can_view_own_checkins(view_func):
    """Có quyền xem checkins của mình"""
    return permission_required('checkin.can_view_own_checkins')(view_func)
