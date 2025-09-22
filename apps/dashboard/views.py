from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from apps.checkin.models import Checkin
from apps.area.models import Area
from apps.users.models import User, UserRole
from apps.checkin.decorators import role_required


@login_required
def dashboard_main_view(request):
    """Router chính cho dashboard"""
    user = request.user
    
    # Redirect based on user role
    if user.role == UserRole.ADMIN:
        return redirect('dashboard:manager')
    elif user.role == UserRole.MANAGER:
        return redirect('dashboard:manager')
    elif user.role == UserRole.HCNS:
        return redirect('dashboard:hr')
    else:
        return redirect('dashboard:personal')


@login_required
def dashboard_personal_view(request):
    """Dashboard cá nhân cho nhân viên"""
    user = request.user
    
    # Thống kê check-in của nhân viên
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Check-ins hôm nay
    today_checkins = Checkin.objects.filter(
        user=user,
        created_at__date=today
    ).count()
    
    # Check-ins tuần này
    week_checkins = Checkin.objects.filter(
        user=user,
        created_at__date__gte=week_start
    ).count()
    
    # Check-ins tháng này
    month_checkins = Checkin.objects.filter(
        user=user,
        created_at__date__gte=month_start
    ).count()
    
    # Check-ins gần đây
    recent_checkins = Checkin.objects.filter(user=user).select_related('area').order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'month_checkins': month_checkins,
        'recent_checkins': recent_checkins,
    }
    return render(request, 'dashboard/personal.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER])
def dashboard_manager_view(request):
    """Dashboard cho quản lý"""
    # Thống kê tổng quan
    total_employees = User.objects.filter(role=UserRole.EMPLOYEE, is_active=True).count()
    total_areas = Area.objects.filter(is_active=True).count()
    
    # Thống kê check-in hôm nay
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Thống kê check-in tuần này
    week_start = today - timedelta(days=today.weekday())
    week_checkins = Checkin.objects.filter(created_at__date__gte=week_start).count()
    
    # Thống kê theo phòng ban
    from apps.users.models import Department
    department_stats = Department.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')
    
    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_areas': total_areas,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'department_stats': department_stats,
        'recent_checkins': recent_checkins,
    }
    return render(request, 'dashboard/manager.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def dashboard_hr_view(request):
    """Dashboard nhân sự cho HCNS"""
    # Thống kê nhân viên
    total_employees = User.objects.filter(role=UserRole.EMPLOYEE).count()
    active_employees = User.objects.filter(role=UserRole.EMPLOYEE, is_active=True).count()
    inactive_employees = total_employees - active_employees
    
    # Thống kê theo phòng ban
    from apps.users.models import Department
    department_stats = Department.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-employee_count')
    
    # Thống kê check-in
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:10]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'department_stats': department_stats,
        'today_checkins': today_checkins,
        'recent_checkins': recent_checkins,
    }
    return render(request, 'dashboard/hr.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def dashboard_secretary_view(request):
    """Dashboard cho thư ký"""
    # Thống kê khu vực
    total_areas = Area.objects.count()
    active_areas = Area.objects.filter(is_active=True).count()
    
    # Thống kê check-in
    today = timezone.now().date()
    today_checkins = Checkin.objects.filter(created_at__date=today).count()
    
    # Thống kê theo khu vực
    area_stats = Area.objects.annotate(
        checkin_count=Count('checkin')
    ).order_by('-checkin_count')
    
    # Check-ins gần đây
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:10]
    
    context = {
        'total_areas': total_areas,
        'active_areas': active_areas,
        'today_checkins': today_checkins,
        'area_stats': area_stats,
        'recent_checkins': recent_checkins,
    }
    return render(request, 'dashboard/secretary.html', context)