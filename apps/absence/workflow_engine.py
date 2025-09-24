from django.utils import timezone
from django.db import models
from .models import AbsenceRequest, ApprovalHistory
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


class WorkflowEngine:
    """Engine xử lý workflow phê duyệt"""
    
    @staticmethod
    def get_next_approver(absence_request):
        """Lấy người phê duyệt tiếp theo"""
        workflow = absence_request.workflow
        department = absence_request.user.department
        office = department.office if department else None
        
        # Kiểm tra từng cấp theo thứ tự ưu tiên
        approvers = []
        
        # 1. Department Manager/Deputy
        if workflow.requires_department_manager:
            if department and department.manager:
                if not WorkflowEngine._is_absent(department.manager, absence_request.start_date, absence_request.end_date):
                    approvers.append({
                        'user': department.manager,
                        'level': 'department_manager',
                        'priority': workflow.department_manager_priority
                    })
            elif workflow.requires_department_deputy and department and department.deputy_manager:
                if not WorkflowEngine._is_absent(department.deputy_manager, absence_request.start_date, absence_request.end_date):
                    approvers.append({
                        'user': department.deputy_manager,
                        'level': 'department_deputy',
                        'priority': workflow.department_deputy_priority
                    })
        
        # 2. Office Director/Deputy
        if workflow.requires_office_director and office:
            if office.director and not WorkflowEngine._is_absent(office.director, absence_request.start_date, absence_request.end_date):
                approvers.append({
                    'user': office.director,
                    'level': 'office_director',
                    'priority': workflow.office_director_priority
                })
            elif workflow.requires_office_deputy and office.deputy_director:
                if not WorkflowEngine._is_absent(office.deputy_director, absence_request.start_date, absence_request.end_date):
                    approvers.append({
                        'user': office.deputy_director,
                        'level': 'office_deputy',
                        'priority': workflow.office_deputy_priority
                    })
        
        # 3. HR (nếu cần)
        if workflow.requires_hr_approval:
            from apps.users.models import User
            hr_users = User.objects.filter(role='hr', is_active=True)
            for hr in hr_users:
                if not WorkflowEngine._is_absent(hr, absence_request.start_date, absence_request.end_date):
                    approvers.append({
                        'user': hr,
                        'level': 'hr',
                        'priority': 5
                    })
        
        # Sắp xếp theo priority và trả về người đầu tiên
        approvers.sort(key=lambda x: x['priority'])
        return approvers[0] if approvers else None
    
    @staticmethod
    def _is_absent(user, start_date, end_date):
        """Kiểm tra user có vắng mặt trong khoảng thời gian không"""
        return AbsenceRequest.objects.filter(
            user=user,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()
    
    @staticmethod
    def process_approval(absence_request, approver, action, comment=''):
        """Xử lý phê duyệt"""
        # Lưu lịch sử
        ApprovalHistory.objects.create(
            absence_request=absence_request,
            approver=approver,
            action=action,
            level=absence_request.approval_level,
            comment=comment
        )
        
        if action == 'approved':
            # Kiểm tra có cần phê duyệt thêm không
            next_approver = WorkflowEngine.get_next_approver(absence_request)
            if next_approver:
                # Chuyển cho người tiếp theo
                absence_request.current_approver = next_approver['user']
                absence_request.approval_level = next_approver['level']
                absence_request.save()
                
                # Gửi thông báo
                NotificationService.send_approval_notification(absence_request, next_approver['user'])
            else:
                # Hoàn thành workflow
                absence_request.status = 'approved'
                absence_request.approved_by = approver
                absence_request.approved_at = timezone.now()
                absence_request.current_approver = None
                absence_request.save()
                
                # Gửi thông báo hoàn thành
                NotificationService.send_completion_notification(absence_request)
        
        elif action == 'rejected':
            absence_request.status = 'rejected'
            absence_request.approved_by = approver
            absence_request.approved_at = timezone.now()
            absence_request.rejection_reason = comment
            absence_request.current_approver = None
            absence_request.save()
            
            # Gửi thông báo từ chối
            NotificationService.send_rejection_notification(absence_request)
    
    @staticmethod
    def create_absence_request(user, absence_type, start_date, end_date, start_time=None, end_time=None, reason='', attachment=None):
        """Tạo đơn vắng mặt mới"""
        from .models import ApprovalWorkflow
        
        # Tính tổng số ngày
        total_days = WorkflowEngine._calculate_total_days(start_date, end_date, start_time, end_time)
        
        # Lấy workflow cho phòng ban và loại vắng mặt
        try:
            workflow = ApprovalWorkflow.objects.get(
                department=user.department,
                absence_type=absence_type,
                is_active=True
            )
        except ApprovalWorkflow.DoesNotExist:
            # Tạo workflow mặc định nếu chưa có
            workflow = ApprovalWorkflow.objects.create(
                department=user.department,
                absence_type=absence_type,
                requires_department_manager=True,
                requires_hr_approval=True
            )
        
        # Tạo đơn vắng mặt
        absence_request = AbsenceRequest.objects.create(
            user=user,
            absence_type=absence_type,
            workflow=workflow,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            total_days=total_days,
            reason=reason,
            attachment=attachment
        )
        
        # Lấy người phê duyệt đầu tiên
        next_approver = WorkflowEngine.get_next_approver(absence_request)
        if next_approver:
            absence_request.current_approver = next_approver['user']
            absence_request.approval_level = next_approver['level']
            absence_request.save()
            
            # Gửi thông báo
            NotificationService.send_approval_notification(absence_request, next_approver['user'])
        else:
            # Tự động duyệt nếu không cần phê duyệt
            absence_request.status = 'approved'
            absence_request.approved_at = timezone.now()
            absence_request.save()
            
            NotificationService.send_completion_notification(absence_request)
        
        return absence_request
    
    @staticmethod
    def _calculate_total_days(start_date, end_date, start_time=None, end_time=None):
        """Tính tổng số ngày nghỉ"""
        from datetime import timedelta
        
        # Tính số ngày cơ bản
        total_days = (end_date - start_date).days + 1
        
        # Nếu có thời gian cụ thể, tính theo giờ
        if start_time and end_time:
            # Tính số giờ nghỉ trong ngày
            start_hour = start_time.hour + start_time.minute / 60
            end_hour = end_time.hour + end_time.minute / 60
            
            # Nếu nghỉ nửa ngày (4 giờ)
            if end_hour - start_hour <= 4:
                total_days = 0.5
            else:
                total_days = 1
        
        return total_days
    
    @staticmethod
    def check_overdue_requests():
        """Kiểm tra và xử lý các đơn quá hạn"""
        overdue_requests = AbsenceRequest.objects.filter(
            status='pending',
            created_at__lt=timezone.now() - timezone.timedelta(hours=24)  # Quá 24 giờ
        )
        
        for request in overdue_requests:
            if request.is_overdue:
                # Gửi thông báo nhắc nhở
                NotificationService.send_reminder_notification(request, request.current_approver, 1)
    
    @staticmethod
    def get_workflow_status(absence_request):
        """Lấy trạng thái workflow hiện tại"""
        if absence_request.status == 'pending':
            level_map = {
                'department_manager': 'Trưởng phòng',
                'department_deputy': 'Phó phòng',
                'office_director': 'Giám đốc VP',
                'office_deputy': 'Phó GĐ VP',
                'hr': 'HR'
            }
            current_level = level_map.get(absence_request.approval_level, 'Không xác định')
            return f"Chờ phê duyệt từ {current_level}"
        elif absence_request.status == 'approved':
            return "Đã được phê duyệt"
        elif absence_request.status == 'rejected':
            return "Đã bị từ chối"
        else:
            return "Đã hủy"
