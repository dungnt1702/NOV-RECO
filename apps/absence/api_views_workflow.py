from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import AbsenceType, ApprovalWorkflow
from apps.users.models import Department


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workflow_api(request):
    """API quản lý workflow"""
    if request.method == 'GET':
        # Lấy danh sách workflow
        workflows = ApprovalWorkflow.objects.select_related('department', 'absence_type').all()
        data = []
        for workflow in workflows:
            data.append({
                'id': workflow.id,
                'department_id': workflow.department.id,
                'department_name': workflow.department.full_name,
                'absence_type_id': workflow.absence_type.id,
                'absence_type_name': workflow.absence_type.name,
                'requires_department_manager': workflow.requires_department_manager,
                'requires_department_deputy': workflow.requires_department_deputy,
                'requires_office_director': workflow.requires_office_director,
                'requires_office_deputy': workflow.requires_office_deputy,
                'requires_hr_approval': workflow.requires_hr_approval,
                'department_manager_timeout_hours': workflow.department_manager_timeout_hours,
                'department_deputy_timeout_hours': workflow.department_deputy_timeout_hours,
                'office_director_timeout_hours': workflow.office_director_timeout_hours,
                'office_deputy_timeout_hours': workflow.office_deputy_timeout_hours,
                'hr_timeout_hours': workflow.hr_timeout_hours,
                'send_reminder_before_hours': workflow.send_reminder_before_hours,
                'max_reminders': workflow.max_reminders,
                'is_active': workflow.is_active
            })
        return Response(data)
    
    elif request.method == 'POST':
        # Tạo workflow mới
        try:
            data = request.data
            department = get_object_or_404(Department, id=data.get('department'))
            absence_type = get_object_or_404(AbsenceType, id=data.get('absence_type'))
            
            workflow = ApprovalWorkflow.objects.create(
                department=department,
                absence_type=absence_type,
                requires_department_manager=data.get('requires_department_manager', False),
                requires_department_deputy=data.get('requires_department_deputy', False),
                requires_office_director=data.get('requires_office_director', False),
                requires_office_deputy=data.get('requires_office_deputy', False),
                requires_hr_approval=data.get('requires_hr_approval', True),
                department_manager_timeout_hours=data.get('department_manager_timeout_hours', 24),
                department_deputy_timeout_hours=data.get('department_deputy_timeout_hours', 24),
                office_director_timeout_hours=data.get('office_director_timeout_hours', 48),
                office_deputy_timeout_hours=data.get('office_deputy_timeout_hours', 48),
                hr_timeout_hours=data.get('hr_timeout_hours', 48),
                send_reminder_before_hours=data.get('send_reminder_before_hours', 2),
                max_reminders=data.get('max_reminders', 3),
                is_active=data.get('is_active', True)
            )
            
            return Response({
                'success': True,
                'message': 'Workflow đã được tạo thành công',
                'workflow_id': workflow.id
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Lỗi khi tạo workflow: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def workflow_detail_api(request, workflow_id):
    """API chi tiết workflow"""
    workflow = get_object_or_404(ApprovalWorkflow, id=workflow_id)
    
    if request.method == 'GET':
        # Lấy thông tin workflow
        data = {
            'id': workflow.id,
            'department_id': workflow.department.id,
            'department_name': workflow.department.full_name,
            'absence_type_id': workflow.absence_type.id,
            'absence_type_name': workflow.absence_type.name,
            'requires_department_manager': workflow.requires_department_manager,
            'requires_department_deputy': workflow.requires_department_deputy,
            'requires_office_director': workflow.requires_office_director,
            'requires_office_deputy': workflow.requires_office_deputy,
            'requires_hr_approval': workflow.requires_hr_approval,
            'department_manager_timeout_hours': workflow.department_manager_timeout_hours,
            'department_deputy_timeout_hours': workflow.department_deputy_timeout_hours,
            'office_director_timeout_hours': workflow.office_director_timeout_hours,
            'office_deputy_timeout_hours': workflow.office_deputy_timeout_hours,
            'hr_timeout_hours': workflow.hr_timeout_hours,
            'send_reminder_before_hours': workflow.send_reminder_before_hours,
            'max_reminders': workflow.max_reminders,
            'is_active': workflow.is_active
        }
        return Response({'success': True, 'workflow': data})
    
    elif request.method == 'PUT':
        # Cập nhật workflow
        try:
            data = request.data
            workflow.department = get_object_or_404(Department, id=data.get('department'))
            workflow.absence_type = get_object_or_404(AbsenceType, id=data.get('absence_type'))
            workflow.requires_department_manager = data.get('requires_department_manager', False)
            workflow.requires_department_deputy = data.get('requires_department_deputy', False)
            workflow.requires_office_director = data.get('requires_office_director', False)
            workflow.requires_office_deputy = data.get('requires_office_deputy', False)
            workflow.requires_hr_approval = data.get('requires_hr_approval', True)
            workflow.department_manager_timeout_hours = data.get('department_manager_timeout_hours', 24)
            workflow.department_deputy_timeout_hours = data.get('department_deputy_timeout_hours', 24)
            workflow.office_director_timeout_hours = data.get('office_director_timeout_hours', 48)
            workflow.office_deputy_timeout_hours = data.get('office_deputy_timeout_hours', 48)
            workflow.hr_timeout_hours = data.get('hr_timeout_hours', 48)
            workflow.send_reminder_before_hours = data.get('send_reminder_before_hours', 2)
            workflow.max_reminders = data.get('max_reminders', 3)
            workflow.is_active = data.get('is_active', True)
            workflow.save()
            
            return Response({
                'success': True,
                'message': 'Workflow đã được cập nhật thành công'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Lỗi khi cập nhật workflow: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Xóa workflow
        try:
            workflow.delete()
            return Response({
                'success': True,
                'message': 'Workflow đã được xóa thành công'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Lỗi khi xóa workflow: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
