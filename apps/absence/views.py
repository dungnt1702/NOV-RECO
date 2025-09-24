from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import AbsenceType, AbsenceRequest, ApprovalWorkflow, ApprovalHistory
from .workflow_engine import WorkflowEngine
from apps.notifications.services import NotificationService
from apps.users.models import User, Department, Office
from apps.users.permissions import permission_required


@login_required
def absence_request_view(request):
    """Trang tạo đơn vắng mặt"""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            absence_type_id = request.POST.get('absence_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reason = request.POST.get('reason')
            
            # Validate dữ liệu
            if not all([absence_type_id, start_date, end_date, reason]):
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return redirect('absence:request')
            
            # Tạo đơn vắng mặt
            absence_type = get_object_or_404(AbsenceType, id=absence_type_id)
            absence_request = WorkflowEngine.create_absence_request(
                user=request.user,
                absence_type=absence_type,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time if start_time else None,
                end_time=end_time if end_time else None,
                reason=reason
            )
            
            messages.success(request, 'Đơn vắng mặt đã được tạo thành công!')
            return redirect('absence:detail', absence_request.id)
            
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('absence:request')
    
    # GET request - hiển thị form
    absence_types = AbsenceType.objects.filter(is_active=True)
    return render(request, 'absence/request.html', {
        'absence_types': absence_types
    })


@login_required
def absence_list_view(request):
    """Trang danh sách đơn vắng mặt"""
    # Filter theo user và permissions
    if request.user.is_superuser or request.user.is_admin_user:
        absence_requests = AbsenceRequest.objects.all()
    else:
        # Chỉ xem đơn của mình hoặc đơn cần phê duyệt
        absence_requests = AbsenceRequest.objects.filter(
            Q(user=request.user) | Q(current_approver=request.user)
        )
    
    # Filter theo trạng thái
    status_filter = request.GET.get('status')
    if status_filter:
        absence_requests = absence_requests.filter(status=status_filter)
    
    # Filter theo loại vắng mặt
    type_filter = request.GET.get('type')
    if type_filter:
        absence_requests = absence_requests.filter(absence_type_id=type_filter)
    
    # Pagination
    paginator = Paginator(absence_requests.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context data
    absence_types = AbsenceType.objects.filter(is_active=True)
    
    return render(request, 'absence/list.html', {
        'page_obj': page_obj,
        'absence_types': absence_types,
        'current_status': status_filter,
        'current_type': type_filter
    })


@login_required
def absence_detail_view(request, absence_id):
    """Trang chi tiết đơn vắng mặt"""
    absence_request = get_object_or_404(AbsenceRequest, id=absence_id)
    
    # Kiểm tra quyền xem
    if not (request.user.is_superuser or 
            request.user == absence_request.user or 
            request.user == absence_request.current_approver):
        messages.error(request, 'Bạn không có quyền xem đơn này')
        return redirect('absence:list')
    
    # Lấy lịch sử phê duyệt
    approval_history = ApprovalHistory.objects.filter(
        absence_request=absence_request
    ).order_by('-created_at')
    
    return render(request, 'absence/detail.html', {
        'absence_request': absence_request,
        'approval_history': approval_history
    })


@login_required
def approval_view(request):
    """Trang phê duyệt đơn vắng mặt"""
    # Lấy danh sách đơn cần phê duyệt
    pending_requests = AbsenceRequest.objects.filter(
        current_approver=request.user,
        status='pending'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(pending_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'absence/approval.html', {
        'page_obj': page_obj
    })


@login_required
@permission_required('absence.can_manage_absence_types')
def workflow_config_view(request):
    """Trang cấu hình workflow phê duyệt"""
    workflows = ApprovalWorkflow.objects.select_related('department', 'absence_type').all()
    departments = Department.objects.select_related('office').all()
    absence_types = AbsenceType.objects.all()
    
    return render(request, 'absence/workflow_config.html', {
        'workflows': workflows,
        'departments': departments,
        'absence_types': absence_types
    })