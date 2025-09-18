from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from users.models import UserRole


def role_required(allowed_roles):
    """
    Decorator để kiểm tra vai trò người dùng
    allowed_roles: list các vai trò được phép truy cập
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            # Debug logging
            print(f"DEBUG: User: {request.user.username}")
            print(f"DEBUG: Role: {request.user.role}")
            print(f"DEBUG: Is superuser: {request.user.is_superuser}")
            print(f"DEBUG: Allowed roles: {allowed_roles}")

            # Superuser luôn có quyền truy cập
            if request.user.is_superuser:
                print("DEBUG: Superuser access granted")
                return view_func(request, *args, **kwargs)

            if request.user.role not in allowed_roles:
                print(f"DEBUG: Access denied - role {request.user.role} not in {allowed_roles}")
                messages.error(
                    request, "Bạn không có quyền truy cập trang này."
                )
                return redirect("home")

            print("DEBUG: Role access granted")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(view_func):
    """Decorator cho Admin và Superuser"""
    return role_required([UserRole.ADMIN])(view_func)


def manager_required(view_func):
    """Decorator cho Quản lý, Admin và Superuser"""
    return role_required([UserRole.ADMIN, UserRole.MANAGER])(view_func)


def employee_required(view_func):
    """Decorator cho tất cả người dùng đã đăng nhập"""
    return role_required(
        [UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE]
    )(view_func)


def superuser_required(view_func):
    """Decorator chỉ cho Superuser"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account_login")
        
        if not request.user.is_superuser:
            messages.error(
                request, "Chỉ có Superuser mới có quyền truy cập trang này."
            )
            return redirect("home")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_permission(user, permission):
    """
    Kiểm tra quyền cụ thể của người dùng
    """
    if not user.is_authenticated:
        return False

    if permission == "view_all_checkins":
        return user.can_view_all_checkins()
    elif permission == "manage_users":
        return user.can_manage_users()
    elif permission == "manage_locations":
        return user.can_manage_locations()
    elif permission == "checkin":
        return user.is_employee() or user.is_manager() or user.is_admin()

    return False
