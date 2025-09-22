from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User, UserRole, Department
from users.forms import UserCreateForm, UserUpdateForm
from users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .decorators import role_required


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def employee_list_view(request):
    """Danh sách nhân viên cho Quản lý và HCNS"""
    context = {
        "role_choices": UserRole.choices,
        "departments": Department.objects.all().order_by('name'),
    }
    return render(request, "employee/list.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def employee_form_view(request, employee_id=None):
    """Form thêm/sửa nhân viên cho Quản lý và HCNS"""
    employee = None
    if employee_id:
        try:
            employee = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            messages.error(request, "Nhân viên không tồn tại.")
            return redirect("employee:list")
    
    if request.method == "POST":
        if employee:
            form = UserUpdateForm(request.POST, instance=employee)
        else:
            form = UserCreateForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            action = "cập nhật" if employee else "tạo"
            messages.success(request, f"Đã {action} nhân viên {user.username} thành công!")
            return redirect("employee:list")
    else:
        if employee:
            form = UserUpdateForm(instance=employee)
        else:
            form = UserCreateForm()
    
    context = {
        'form': form,
        'employee': employee,
        'title': f"{'Cập nhật' if employee else 'Tạo'} nhân viên",
        'submit_text': f"{'Cập nhật' if employee else 'Tạo'} nhân viên",
    }
    return render(request, "employee/form.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def employee_detail_view(request, employee_id):
    """Chi tiết nhân viên cho Quản lý và HCNS"""
    employee = get_object_or_404(User, id=employee_id)
    
    # Get employee's check-ins
    from .models import Checkin
    checkins = Checkin.objects.filter(user=employee).select_related('area').order_by('-created_at')[:10]
    
    context = {
        'employee': employee,
        'checkins': checkins,
    }
    return render(request, "employee/detail.html", context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def employee_delete_view(request, employee_id):
    """Xóa nhân viên cho Quản lý và HCNS"""
    employee = get_object_or_404(User, id=employee_id)
    
    if request.method == "POST":
        username = employee.username
        employee.delete()
        messages.success(request, f"Đã xóa nhân viên {username} thành công!")
        return redirect("employee:list")
    
    context = {
        'employee': employee,
    }
    return render(request, "employee/delete.html", context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_list_api(request):
    """API danh sách nhân viên"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    role = request.GET.get('role', '')
    department_id = request.GET.get('department_id', '')
    search = request.GET.get('search', '')
    
    # Build queryset
    queryset = User.objects.all().order_by('-date_joined')
    
    # Apply filters
    if role:
        queryset = queryset.filter(role=role)
    if department_id:
        queryset = queryset.filter(department_id=department_id)
    if search:
        queryset = queryset.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize data
    serializer = UserSerializer(page_obj, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def employee_create_api(request):
    """API tạo nhân viên mới"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_detail_api(request, employee_id):
    """API chi tiết nhân viên"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    try:
        employee = User.objects.get(id=employee_id)
        serializer = UserSerializer(employee)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def employee_update_api(request, employee_id):
    """API cập nhật nhân viên"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    try:
        employee = User.objects.get(id=employee_id)
        serializer = UserUpdateSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def employee_delete_api(request, employee_id):
    """API xóa nhân viên"""
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or request.user.is_hcns()):
        return Response({"error": "Permission denied"}, status=403)
    
    try:
        employee = User.objects.get(id=employee_id)
        employee.delete()
        return Response({"message": "Employee deleted successfully"}, status=200)
    except User.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)
