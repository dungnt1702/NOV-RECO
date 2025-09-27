from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect

from .models import Department, Office, User


def office_manager_required(view_func):
    """
    Decorator yêu cầu user phải là Office Director hoặc Deputy Director
    để có thể truy cập dữ liệu của văn phòng đó.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superuser và Admin có thể truy cập tất cả
        if user.is_superuser or user.is_admin_user():
            return view_func(request, *args, **kwargs)

        # Lấy office_id từ kwargs hoặc request
        office_id = kwargs.get("office_id") or request.GET.get("office_id")

        if office_id:
            try:
                office = Office.objects.get(id=office_id)
                if user.can_view_office_data(office):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(
                        request,
                        "Bạn không có quyền truy cập dữ liệu của văn phòng này.",
                    )
                    return redirect("users:office_list")
            except Office.DoesNotExist:
                raise Http404("Văn phòng không tồn tại")

        # Nếu không có office_id, kiểm tra xem user có quản lý văn phòng nào không
        managed_offices = user.get_managed_offices()
        if managed_offices.exists():
            return view_func(request, *args, **kwargs)

        messages.error(request, "Bạn không có quyền truy cập dữ liệu văn phòng.")
        return redirect("users:office_list")

    return wrapper


def department_manager_required(view_func):
    """
    Decorator yêu cầu user phải là Department Manager hoặc Deputy Manager
    để có thể truy cập dữ liệu của phòng ban đó.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superuser và Admin có thể truy cập tất cả
        if user.is_superuser or user.is_admin_user():
            return view_func(request, *args, **kwargs)

        # Lấy department_id từ kwargs hoặc request
        department_id = kwargs.get("department_id") or request.GET.get("department_id")

        if department_id:
            try:
                department = Department.objects.get(id=department_id)
                if user.can_view_department_data(department):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(
                        request,
                        "Bạn không có quyền truy cập dữ liệu của phòng ban này.",
                    )
                    return redirect("users:department_list")
            except Department.DoesNotExist:
                raise Http404("Phòng ban không tồn tại")

        # Nếu không có department_id, kiểm tra xem user có quản lý phòng ban nào không
        managed_departments = user.get_managed_departments()
        if managed_departments.exists():
            return view_func(request, *args, **kwargs)

        messages.error(request, "Bạn không có quyền truy cập dữ liệu phòng ban.")
        return redirect("users:department_list")

    return wrapper


def hr_or_manager_required(view_func):
    """
    Decorator yêu cầu user phải là HR hoặc Manager (ở bất kỳ cấp nào)
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superuser và Admin có thể truy cập tất cả
        if user.is_superuser or user.is_admin_user():
            return view_func(request, *args, **kwargs)

        # HR có thể truy cập
        if user.is_hr_user():
            return view_func(request, *args, **kwargs)

        # Manager ở bất kỳ cấp nào có thể truy cập
        if (
            user.is_office_director()
            or user.is_office_deputy_director()
            or user.is_department_manager()
            or user.is_department_deputy_manager()
        ):
            return view_func(request, *args, **kwargs)

        messages.error(request, "Bạn không có quyền truy cập chức năng này.")
        return redirect("dashboard:index")

    return wrapper


def absence_approval_required(view_func):
    """
    Decorator yêu cầu user có quyền phê duyệt đơn vắng mặt
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Superuser và Admin có thể phê duyệt tất cả
        if user.is_superuser or user.is_admin_user():
            return view_func(request, *args, **kwargs)

        # HR có thể phê duyệt
        if user.is_hr_user():
            return view_func(request, *args, **kwargs)

        # Manager có thể phê duyệt đơn của phòng ban/văn phòng họ quản lý
        if (
            user.is_office_director()
            or user.is_office_deputy_director()
            or user.is_department_manager()
            or user.is_department_deputy_manager()
        ):
            return view_func(request, *args, **kwargs)

        messages.error(request, "Bạn không có quyền phê duyệt đơn vắng mặt.")
        return redirect("absence:list")

    return wrapper


def data_isolation_mixin(view_func):
    """
    Mixin để áp dụng data isolation cho views
    Tự động filter dữ liệu dựa trên quyền của user
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Thêm thông tin user vào request để views có thể sử dụng
        request.user_permissions = {
            "is_superuser": user.is_superuser,
            "is_admin": user.is_admin_user(),
            "is_hr": user.is_hr_user(),
            "is_office_director": user.is_office_director(),
            "is_office_deputy": user.is_office_deputy_director(),
            "is_department_manager": user.is_department_manager(),
            "is_department_deputy": user.is_department_deputy_manager(),
            "managed_offices": list(
                user.get_managed_offices().values_list("id", flat=True)
            ),
            "managed_departments": list(
                user.get_managed_departments().values_list("id", flat=True)
            ),
        }

        return view_func(request, *args, **kwargs)

    return wrapper


def check_absence_permission(user, absence_request):
    """
    Kiểm tra xem user có quyền thao tác với absence_request không
    """
    # Superuser và Admin có thể thao tác tất cả
    if user.is_superuser or user.is_admin_user():
        return True

    # Người tạo đơn có thể xem và hủy đơn của mình
    if absence_request.user == user:
        return True

    # HR có thể thao tác tất cả đơn
    if user.is_hr_user():
        return True

    # Manager có thể thao tác đơn của phòng ban/văn phòng họ quản lý
    if absence_request.user.department:
        if user.can_view_department_data(absence_request.user.department):
            return True

    return False


def check_approval_permission(user, absence_request):
    """
    Kiểm tra xem user có quyền phê duyệt absence_request không
    """
    # Superuser và Admin có thể phê duyệt tất cả
    if user.is_superuser or user.is_admin_user():
        return True

    # HR có thể phê duyệt tất cả
    if user.is_hr_user():
        return True

    # Manager có thể phê duyệt đơn của phòng ban/văn phòng họ quản lý
    if absence_request.user.department:
        if user.can_approve_absence_for_department(absence_request.user.department):
            return True

    return False
