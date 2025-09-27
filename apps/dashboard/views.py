from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.checkin.models import Checkin
from apps.location.models import Location
from apps.users.models import User, UserRole
from apps.users.permissions import group_required


@login_required
def dashboard_main_view(request):
    """Trang chủ tổng quan"""
    user = request.user
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Thống kê cơ bản cho tất cả vai trò
    context = {
        "user": user,
        "user_role": user.role,
        "today": today,
        "now": timezone.now(),
    }

    # Thống kê check-in hôm nay
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    context["today_checkins"] = today_checkins

    # Thống kê check-in tuần này
    week_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    context["week_checkins"] = week_checkins

    # Thống kê check-in tháng này
    month_checkins = Checkin.objects.filter(created_at__date__gte=month_start).count()
    context["month_checkins"] = month_checkins

    # Thống kê theo vai trò
    if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS]:
        # Thống kê tổng quan cho quản lý
        total_employees = User.objects.filter(is_active=True).count()
        total_areas = Location.objects.filter(is_active=True).count()

        # Thống kê theo phòng ban
        from apps.users.models import Department
        all_departments = Department.objects.all()
        department_stats = all_departments.annotate(
            employee_count=Count("user")
        ).order_by("-employee_count")[:5]

        # Check-ins gần đây
        recent_checkins = Checkin.objects.select_related("user", "location").order_by("-created_at")[:10]

        context.update({
            "total_employees": total_employees,
            "total_areas": total_areas,
            "total_departments": all_departments.count(),
            "department_stats": department_stats,
            "recent_checkins": recent_checkins,
        })
    else:
        # Thống kê cá nhân cho nhân viên
        user_today_checkins = Checkin.objects.filter(user=user, created_at__date=today).count()
        user_week_checkins = Checkin.objects.filter(user=user, created_at__date__gte=week_start).count()
        user_month_checkins = Checkin.objects.filter(user=user, created_at__date__gte=month_start).count()

        # Check-ins gần đây của user
        user_recent_checkins = (
            Checkin.objects.filter(user=user)
            .select_related("location")
            .order_by("-created_at")[:5]
        )

        context.update({
            "user_today_checkins": user_today_checkins,
            "user_week_checkins": user_week_checkins,
            "user_month_checkins": user_month_checkins,
            "user_recent_checkins": user_recent_checkins,
            "total_employees": 0,
            "total_areas": 0,
            "total_departments": 0,
            "department_stats": [],
        })

    return render(request, "dashboard/main.html", context)


@login_required
def dashboard_personal_view(request):
    """Dashboard cá nhân cho nhân viên"""
    user = request.user
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Thống kê check-in của nhân viên
    today_checkins = Checkin.objects.filter(user=user, created_at__date=today).count()
    week_checkins = Checkin.objects.filter(user=user, created_at__date__gte=week_start).count()
    month_checkins = Checkin.objects.filter(user=user, created_at__date__gte=month_start).count()

    # Check-ins gần đây
    recent_checkins = (
        Checkin.objects.filter(user=user)
        .select_related("location")
        .order_by("-created_at")[:5]
    )

    # Tính thời gian làm việc hôm nay
    work_hours = "0h"  # TODO: Implement work hours calculation
    
    # Vị trí hiện tại
    current_location = "Chưa xác định"  # TODO: Get current location
    
    # Thông báo gần đây
    from apps.notifications.models import Notification
    recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]

    context = {
        "user": user,
        "today": today,
        "today_checkins": today_checkins,
        "week_checkins": week_checkins,
        "month_checkins": month_checkins,
        "work_hours": work_hours,
        "current_location": current_location,
        "recent_checkins": recent_checkins,
        "recent_notifications": recent_notifications,
    }
    return render(request, "dashboard/personal.html", context)


@login_required
def dashboard_management_view(request):
    """Dashboard quản lý cho admin/manager/hcns"""
    user = request.user
    
    # Kiểm tra quyền truy cập
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS]:
        return redirect('dashboard:personal')
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Thống kê tổng quan
    total_employees = User.objects.filter(is_active=True).count()
    total_areas = Location.objects.filter(is_active=True).count()
    
    # Thống kê check-in
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    week_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    
    # Tính tỷ lệ điểm danh
    attendance_rate = 85  # TODO: Calculate actual attendance rate
    online_employees = 12  # TODO: Calculate online employees
    online_percentage = (online_employees / total_employees * 100) if total_employees > 0 else 0
    late_employees = 3  # TODO: Calculate late employees

    # Thống kê theo phòng ban
    from apps.users.models import Department
    department_stats = Department.objects.annotate(
        employee_count=Count("user")
    ).order_by("-employee_count")[:5]

    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related("user", "location").order_by("-created_at")[:10]

    context = {
        "user": user,
        "today": today,
        "total_employees": total_employees,
        "total_areas": total_areas,
        "today_checkins": today_checkins,
        "week_checkins": week_checkins,
        "attendance_rate": attendance_rate,
        "online_employees": online_employees,
        "online_percentage": online_percentage,
        "late_employees": late_employees,
        "department_stats": department_stats,
        "recent_checkins": recent_checkins,
    }
    return render(request, "dashboard/management.html", context)


@group_required(["Super Admin", "Admin", "Manager", "HR"])
def dashboard_hr_view(request):
    """Dashboard nhân sự cho HCNS"""
    # Thống kê nhân viên
    total_employees = User.objects.filter(role=UserRole.EMPLOYEE).count()
    active_employees = User.objects.filter(
        role=UserRole.EMPLOYEE, is_active=True
    ).count()
    inactive_employees = total_employees - active_employees

    # Thống kê theo phòng ban
    from apps.users.models import Department

    department_stats = Department.objects.annotate(
        employee_count=Count("user")
    ).order_by("-employee_count")

    # Thống kê check-in
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Số nhân viên đã check-in hôm nay
    employees_with_checkin_today = Checkin.objects.filter(
        created_at__date=today
    ).values('user').distinct().count()

    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related("user", "location").order_by(
        "-created_at"
    )[:10]

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "department_stats": department_stats,
        "today_checkins": today_checkins,
        "employees_with_checkin_today": employees_with_checkin_today,
        "recent_checkins": recent_checkins,
    }
    return render(request, "dashboard/hr.html", context)


@group_required(["Super Admin", "Admin", "Manager", "Secretary"])
def dashboard_secretary_view(request):
    """Dashboard cho thư ký"""
    # Thống kê địa điểm
    total_areas = Location.objects.count()
    active_areas = Location.objects.filter(is_active=True).count()

    # Thống kê check-in
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()

    # Thống kê theo địa điểm
    area_stats = Location.objects.annotate(checkin_count=Count("checkin")).order_by(
        "-checkin_count"
    )

    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related("user", "location").order_by(
        "-created_at"
    )[:10]

    context = {
        "total_areas": total_areas,
        "active_areas": active_areas,
        "today_checkins": today_checkins,
        "area_stats": area_stats,
        "recent_checkins": recent_checkins,
    }
    return render(request, "dashboard/secretary.html", context)
