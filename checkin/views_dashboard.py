from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Checkin, Area
from users.models import User, UserRole
from .decorators import role_required


@login_required
def dashboard_main_view(request):
    """Router chính cho dashboard dựa trên vai trò người dùng"""
    user = request.user

    if user.is_admin():
        # Admin có thể xem tất cả dashboard
        return redirect("dashboard:manager")
    elif user.is_manager():
        return redirect("dashboard:manager")
    elif user.is_hcns():
        return redirect("dashboard:hr")
    elif user.is_employee():
        return redirect("dashboard:personal")
    else:
        messages.error(request, "Vai trò người dùng không hợp lệ.")
        return redirect("home")


@login_required
def dashboard_personal_view(request):
    """Dashboard cá nhân cho Nhân viên"""
    user = request.user
    
    # Lấy check-in gần nhất
    recent_checkin = Checkin.objects.filter(user=user).order_by('-created_at').first()
    
    # Thống kê cá nhân
    total_checkins = Checkin.objects.filter(user=user).count()
    
    # Check-in trong tháng này
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_checkins = Checkin.objects.filter(
        user=user, 
        created_at__gte=month_start
    ).count()
    
    # Check-in trong tuần này
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_checkins = Checkin.objects.filter(
        user=user, 
        created_at__gte=week_start
    ).count()
    
    # Lịch sử check-in gần đây
    recent_checkins = Checkin.objects.filter(user=user).select_related('area').order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'recent_checkin': recent_checkin,
        'total_checkins': total_checkins,
        'monthly_checkins': monthly_checkins,
        'weekly_checkins': weekly_checkins,
        'recent_checkins': recent_checkins,
    }
    return render(request, "dashboard/personal.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def dashboard_secretary_view(request):
    """Dashboard thư ký"""
    # Thống kê tổng quan
    total_areas = Area.objects.count()
    active_areas = Area.objects.filter(is_active=True).count()
    
    # Check-in hôm nay
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Check-in trong tuần
    week_start = today - timedelta(days=today.weekday())
    week_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    
    # Check-in gần đây
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:10]
    
    # Thống kê theo khu vực
    area_stats = Area.objects.annotate(
        checkin_count=Count('checkin')
    ).order_by('-checkin_count')[:5]
    
    context = {
        'total_areas': total_areas,
        'active_areas': active_areas,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'recent_checkins': recent_checkins,
        'area_stats': area_stats,
    }
    return render(request, "dashboard/secretary.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def dashboard_hr_view(request):
    """Dashboard nhân sự cho HCNS"""
    # Thống kê nhân viên
    total_employees = User.objects.filter(role=UserRole.EMPLOYEE).count()
    total_managers = User.objects.filter(role=UserRole.MANAGER).count()
    total_hcns = User.objects.filter(role=UserRole.HCNS).count()
    
    # Nhân viên mới trong tháng
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_employees = User.objects.filter(
        date_joined__gte=month_start,
        role=UserRole.EMPLOYEE
    ).count()
    
    # Thống kê theo phòng ban
    from users.models import Department
    department_stats = Department.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')
    
    # Check-in hôm nay
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Nhân viên có check-in hôm nay
    employees_with_checkin_today = User.objects.filter(
        checkin__created_at__date=today,
        role=UserRole.EMPLOYEE
    ).distinct().count()
    
    # Tỷ lệ check-in
    checkin_rate = (employees_with_checkin_today / total_employees * 100) if total_employees > 0 else 0
    
    context = {
        'total_employees': total_employees,
        'total_managers': total_managers,
        'total_hcns': total_hcns,
        'new_employees': new_employees,
        'department_stats': department_stats,
        'today_checkins': today_checkins,
        'employees_with_checkin_today': employees_with_checkin_today,
        'checkin_rate': round(checkin_rate, 1),
    }
    return render(request, "dashboard/hr.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER])
def dashboard_manager_view(request):
    """Dashboard quản lý - có thể xem tất cả"""
    # Thống kê tổng quan
    total_users = User.objects.count()
    total_checkins = Checkin.objects.count()
    total_areas = Area.objects.count()
    
    # Thống kê theo vai trò
    users_by_role = {
        'admin': User.objects.filter(role=UserRole.ADMIN).count(),
        'manager': User.objects.filter(role=UserRole.MANAGER).count(),
        'hcns': User.objects.filter(role=UserRole.HCNS).count(),
        'employee': User.objects.filter(role=UserRole.EMPLOYEE).count(),
    }
    
    # Check-in hôm nay
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Check-in trong tuần
    week_start = today - timedelta(days=today.weekday())
    week_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    
    # Check-in gần đây
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:10]
    
    # Thống kê theo khu vực
    area_stats = Area.objects.annotate(
        checkin_count=Count('checkin')
    ).order_by('-checkin_count')[:5]
    
    # Thống kê theo phòng ban
    from users.models import Department
    department_stats = Department.objects.annotate(
        employee_count=Count('employees'),
        checkin_count=Count('employees__checkin')
    ).order_by('-employee_count')
    
    context = {
        'total_users': total_users,
        'total_checkins': total_checkins,
        'total_areas': total_areas,
        'users_by_role': users_by_role,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'recent_checkins': recent_checkins,
        'area_stats': area_stats,
        'department_stats': department_stats,
    }
    return render(request, "dashboard/manager.html", context)
