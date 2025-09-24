from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import AbsenceType, AbsenceRequest, ApprovalWorkflow
from .workflow_engine import WorkflowEngine


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def absence_types_api(request):
    """API lấy danh sách loại vắng mặt"""
    absence_types = AbsenceType.objects.filter(is_active=True)
    data = [
        {
            'id': at.id,
            'name': at.name,
            'code': at.code,
            'description': at.description,
            'requires_approval': at.requires_approval,
            'max_days_per_year': at.max_days_per_year,
            'color': at.color
        }
        for at in absence_types
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def absence_requests_api(request):
    """API lấy danh sách đơn vắng mặt"""
    # Filter theo user và permissions
    if request.user.is_superuser or request.user.is_admin_user:
        absence_requests = AbsenceRequest.objects.select_related('user', 'absence_type', 'workflow').all()
    else:
        absence_requests = AbsenceRequest.objects.select_related('user', 'absence_type', 'workflow').filter(
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
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    absence_requests_page = absence_requests[start:end]
    
    data = [
        {
            'id': ar.id,
            'user_name': ar.user.get_full_name(),
            'absence_type': ar.absence_type.name,
            'start_date': ar.start_date.isoformat(),
            'end_date': ar.end_date.isoformat(),
            'total_days': float(ar.total_days),
            'status': ar.status,
            'status_display': ar.status_display,
            'created_at': ar.created_at.isoformat(),
            'current_approver': ar.current_approver.get_full_name() if ar.current_approver else None,
            'approval_level': ar.approval_level,
            'is_overdue': ar.is_overdue
        }
        for ar in absence_requests_page
    ]
    
    return Response({
        'data': data,
        'total': absence_requests.count(),
        'has_next': end < absence_requests.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_absence_request_api(request):
    """API tạo đơn vắng mặt"""
    try:
        absence_type_id = request.data.get('absence_type_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        reason = request.data.get('reason')
        
        if not all([absence_type_id, start_date, end_date, reason]):
            return Response({
                'error': 'Vui lòng điền đầy đủ thông tin bắt buộc'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        absence_type = get_object_or_404(AbsenceType, id=absence_type_id)
        absence_request = WorkflowEngine.create_absence_request(
            user=request.user,
            absence_type=absence_type,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason
        )
        
        return Response({
            'success': True,
            'absence_request_id': absence_request.id,
            'message': 'Đơn vắng mặt đã được tạo thành công'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_request_api(request, absence_id):
    """API phê duyệt đơn vắng mặt"""
    try:
        absence_request = get_object_or_404(AbsenceRequest, id=absence_id)
        
        if absence_request.current_approver != request.user:
            return Response({
                'error': 'Bạn không có quyền phê duyệt đơn này'
            }, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action')
        comment = request.data.get('comment', '')
        
        if action not in ['approved', 'rejected']:
            return Response({
                'error': 'Hành động không hợp lệ'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        WorkflowEngine.process_approval(absence_request, request.user, action, comment)
        
        return Response({
            'success': True,
            'message': f'Đơn vắng mặt đã được {action}'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_status_api(request, absence_id):
    """API lấy trạng thái workflow"""
    try:
        absence_request = get_object_or_404(AbsenceRequest, id=absence_id)
        
        # Kiểm tra quyền xem
        if not (request.user.is_superuser or 
                request.user == absence_request.user or 
                request.user == absence_request.current_approver):
            return Response({
                'error': 'Bạn không có quyền xem đơn này'
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_info = WorkflowEngine.get_workflow_status(absence_request)
        
        return Response({
            'status': absence_request.status,
            'status_display': absence_request.status_display,
            'workflow_status': status_info,
            'current_approver': absence_request.current_approver.get_full_name() if absence_request.current_approver else None,
            'approval_level': absence_request.approval_level,
            'is_overdue': absence_request.is_overdue
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
