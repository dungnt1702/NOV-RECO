from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User, UserRole, Department
from apps.users.forms import UserCreateForm, UserUpdateForm
from apps.users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from apps.users.permissions import permission_required


@permission_required('users.can_view_users')
def employee_list_view(request):
    """Danh sách nhân viên"""
    employees = User.objects.filter(role=UserRole.EMPLOYEE).order_by('-date_joined')
    
    # Filter by department
    dept_filter = request.GET.get('department')
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.all()
    
    context = {
        'employees': page_obj,
        'departments': departments,
        'current_dept': dept_filter,
        'current_search': search,
    }
    return render(request, 'employee/list.html', context)


@permission_required('users.can_view_users')
def employee_create_view(request):
    """Tạo nhân viên mới"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = UserRole.EMPLOYEE
            user.save()
            messages.success(request, f'Tạo nhân viên {user.get_full_name()} thành công!')
            return redirect('employee:list')
    else:
        form = UserCreateForm()
    
    departments = Department.objects.all()
    context = {
        'form': form,
        'departments': departments,
    }
    return render(request, 'employee/create.html', context)


@permission_required('users.can_view_users')
def employee_update_view(request, employee_id):
    """Cập nhật thông tin nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cập nhật thông tin {employee.get_full_name()} thành công!')
            return redirect('employee:list')
    else:
        form = UserUpdateForm(instance=employee)
    
    departments = Department.objects.all()
    context = {
        'form': form,
        'employee': employee,
        'departments': departments,
    }
    return render(request, 'employee/update.html', context)


@permission_required('users.can_view_users')
def employee_detail_view(request, employee_id):
    """Chi tiết nhân viên cho Quản lý và HCNS"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    # Get employee's check-ins
    from apps.checkin.models import Checkin
    checkins = Checkin.objects.filter(user=employee).select_related('area').order_by('-created_at')[:10]
    
    context = {
        'employee': employee,
        'checkins': checkins,
    }
    return render(request, 'employee/detail.html', context)


@permission_required('users.can_view_users')
def employee_toggle_active_view(request, employee_id):
    """Bật/tắt trạng thái hoạt động của nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    if request.method == 'POST':
        employee.is_active = not employee.is_active
        employee.save()
        
        status_text = "kích hoạt" if employee.is_active else "vô hiệu hóa"
        messages.success(request, f'Đã {status_text} nhân viên {employee.get_full_name()}')
    
    return redirect('employee:list')


@permission_required('users.can_view_users')
def employee_delete_view(request, employee_id):
    """Xóa nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Đã xóa nhân viên {employee_name}')
        return redirect('employee:list')
    
    context = {
        'employee': employee,
    }
    return render(request, 'employee/delete.html', context)


@permission_required('users.can_view_users')
def employee_checkin_history_view(request, employee_id):
    """Lịch sử check-in của nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    from apps.checkin.models import Checkin
    checkins = Checkin.objects.filter(user=employee).select_related('area').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(checkins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employee': employee,
        'checkins': page_obj,
    }
    return render(request, 'employee/checkin_history.html', context)


@permission_required('users.can_view_users')
def employee_statistics_view(request, employee_id):
    """Thống kê nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    
    from apps.checkin.models import Checkin
    from django.utils import timezone
    from datetime import timedelta
    
    # Thống kê check-in
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    today_checkins = Checkin.objects.filter(
        user=employee,
        created_at__date=today
    ).count()
    
    week_checkins = Checkin.objects.filter(
        user=employee,
        created_at__date__gte=week_start
    ).count()
    
    month_checkins = Checkin.objects.filter(
        user=employee,
        created_at__date__gte=month_start
    ).count()
    
    total_checkins = Checkin.objects.filter(user=employee).count()
    
    context = {
        'employee': employee,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'month_checkins': month_checkins,
        'total_checkins': total_checkins,
    }
    return render(request, 'employee/statistics.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_list_api(request):
    """API danh sách nhân viên"""
    employees = User.objects.filter(role=UserRole.EMPLOYEE)
    serializer = UserSerializer(employees, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def employee_create_api(request):
    """API tạo nhân viên"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save(commit=False)
        user.role = UserRole.EMPLOYEE
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def employee_update_api(request, employee_id):
    """API cập nhật nhân viên"""
    employee = get_object_or_404(User, id=employee_id, role=UserRole.EMPLOYEE)
    serializer = UserUpdateSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)