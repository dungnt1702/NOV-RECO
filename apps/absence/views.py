from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.services import NotificationService
from apps.users.models import Department, Office, User
from apps.users.permissions import permission_required

from .models import AbsenceRequest, AbsenceType, ApprovalHistory, ApprovalWorkflow
from .workflow_engine import WorkflowEngine


@login_required
def absence_request_view(request):
    """Trang tạo đơn vắng mặt"""
    if request.method == "POST":
        try:
            # Lấy dữ liệu từ form
            absence_type_id = request.POST.get("absence_type")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            reason = request.POST.get("reason")

            # Validate dữ liệu
            if not all([absence_type_id, start_date, end_date, reason]):
                messages.error(request, "Vui lòng điền đầy đủ thông tin bắt buộc")
                return redirect("absence:request")

            # Tạo đơn vắng mặt
            absence_type = get_object_or_404(AbsenceType, id=absence_type_id)
            absence_request = WorkflowEngine.create_absence_request(
                user=request.user,
                absence_type=absence_type,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time if start_time else None,
                end_time=end_time if end_time else None,
                reason=reason,
            )

            messages.success(request, "Đơn vắng mặt đã được tạo thành công!")
            return redirect("absence:detail", absence_request.id)

        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return redirect("absence:request")

    # GET request - hiển thị form
    absence_types = AbsenceType.objects.filter(is_active=True)
    return render(request, "absence/request.html", {"absence_types": absence_types})


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
    status_filter = request.GET.get("status")
    if status_filter:
        absence_requests = absence_requests.filter(status=status_filter)

    # Filter theo loại vắng mặt
    type_filter = request.GET.get("type")
    if type_filter:
        absence_requests = absence_requests.filter(absence_type_id=type_filter)

    # Pagination
    paginator = Paginator(absence_requests.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Context data
    absence_types = AbsenceType.objects.filter(is_active=True)

    return render(
        request,
        "absence/list.html",
        {
            "page_obj": page_obj,
            "absence_types": absence_types,
            "current_status": status_filter,
            "current_type": type_filter,
        },
    )


@login_required
def absence_history_view(request):
    """Trang lịch sử đơn vắng mặt của người dùng"""
    # Chỉ hiển thị đơn của người dùng đang đăng nhập
    absence_requests = AbsenceRequest.objects.filter(user=request.user)

    # Filter theo trạng thái
    status_filter = request.GET.get("status")
    if status_filter:
        absence_requests = absence_requests.filter(status=status_filter)

    # Filter theo loại vắng mặt
    type_filter = request.GET.get("type")
    if type_filter:
        absence_requests = absence_requests.filter(absence_type_id=type_filter)

    # Pagination
    paginator = Paginator(absence_requests.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Context data
    absence_types = AbsenceType.objects.filter(is_active=True)

    return render(
        request,
        "absence/history.html",
        {
            "page_obj": page_obj,
            "absence_types": absence_types,
            "current_status": status_filter,
            "current_type": type_filter,
        },
    )


@login_required
def absence_detail_view(request, absence_id):
    """Trang chi tiết đơn vắng mặt"""
    absence_request = get_object_or_404(AbsenceRequest, id=absence_id)

    # Kiểm tra quyền xem
    if not (
        request.user.is_superuser
        or request.user == absence_request.user
        or request.user == absence_request.current_approver
    ):
        messages.error(request, "Bạn không có quyền xem đơn này")
        return redirect("absence:list")

    # Lấy lịch sử phê duyệt
    approval_history = ApprovalHistory.objects.filter(
        absence_request=absence_request
    ).order_by("-created_at")

    return render(
        request,
        "absence/detail.html",
        {"absence_request": absence_request, "approval_history": approval_history},
    )


@login_required
def approval_view(request):
    """Trang phê duyệt đơn vắng mặt"""
    # Lấy danh sách đơn cần phê duyệt
    pending_requests = AbsenceRequest.objects.filter(
        current_approver=request.user, status="pending"
    ).order_by("-created_at")

    # Pagination
    paginator = Paginator(pending_requests, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "absence/approval.html", {"page_obj": page_obj})


@login_required
@permission_required("absence.can_manage_absence_types")
def workflow_config_view(request):
    """Trang cấu hình workflow phê duyệt"""
    workflows = ApprovalWorkflow.objects.select_related(
        "department", "absence_type"
    ).all()
    departments = Department.objects.select_related("office").all()
    absence_types = AbsenceType.objects.all()

    return render(
        request,
        "absence/workflow_config.html",
        {
            "workflows": workflows,
            "departments": departments,
            "absence_types": absence_types,
        },
    )


@login_required
@permission_required("absence.can_manage_absence_types")
def workflow_create_view(request):
    """Trang tạo workflow mới"""
    if request.method == "POST":
        try:
            data = request.POST
            department = get_object_or_404(Department, id=data.get("department"))
            absence_type = get_object_or_404(AbsenceType, id=data.get("absence_type"))

            workflow = ApprovalWorkflow.objects.create(
                department=department,
                absence_type=absence_type,
                requires_department_manager=data.get("requires_department_manager")
                == "on",
                requires_department_deputy=data.get("requires_department_deputy")
                == "on",
                requires_office_director=data.get("requires_office_director") == "on",
                requires_office_deputy=data.get("requires_office_deputy") == "on",
                requires_hr_approval=data.get("requires_hr_approval") == "on",
                department_manager_timeout_hours=int(
                    data.get("department_manager_timeout_hours", 24)
                ),
                department_deputy_timeout_hours=int(
                    data.get("department_deputy_timeout_hours", 24)
                ),
                office_director_timeout_hours=int(
                    data.get("office_director_timeout_hours", 48)
                ),
                office_deputy_timeout_hours=int(
                    data.get("office_deputy_timeout_hours", 48)
                ),
                hr_timeout_hours=int(data.get("hr_timeout_hours", 48)),
                send_reminder_before_hours=int(
                    data.get("send_reminder_before_hours", 2)
                ),
                max_reminders=int(data.get("max_reminders", 3)),
                is_active=data.get("is_active") == "on",
            )

            messages.success(
                request,
                f"Workflow đã được tạo thành công cho {workflow.department.full_name} - {workflow.absence_type.name}",
            )
            return redirect("absence:workflow_config")

        except Exception as e:
            messages.error(request, f"Lỗi khi tạo workflow: {str(e)}")

    departments = Department.objects.select_related("office").all()
    absence_types = AbsenceType.objects.all()

    return render(
        request,
        "absence/workflow_create.html",
        {"departments": departments, "absence_types": absence_types},
    )


@login_required
@permission_required("absence.can_manage_absence_types")
def workflow_update_view(request, workflow_id):
    """Trang sửa workflow"""
    workflow = get_object_or_404(ApprovalWorkflow, id=workflow_id)

    if request.method == "POST":
        try:
            data = request.POST
            workflow.department = get_object_or_404(
                Department, id=data.get("department")
            )
            workflow.absence_type = get_object_or_404(
                AbsenceType, id=data.get("absence_type")
            )
            workflow.requires_department_manager = (
                data.get("requires_department_manager") == "on"
            )
            workflow.requires_department_deputy = (
                data.get("requires_department_deputy") == "on"
            )
            workflow.requires_office_director = (
                data.get("requires_office_director") == "on"
            )
            workflow.requires_office_deputy = data.get("requires_office_deputy") == "on"
            workflow.requires_hr_approval = data.get("requires_hr_approval") == "on"
            workflow.department_manager_timeout_hours = int(
                data.get("department_manager_timeout_hours", 24)
            )
            workflow.department_deputy_timeout_hours = int(
                data.get("department_deputy_timeout_hours", 24)
            )
            workflow.office_director_timeout_hours = int(
                data.get("office_director_timeout_hours", 48)
            )
            workflow.office_deputy_timeout_hours = int(
                data.get("office_deputy_timeout_hours", 48)
            )
            workflow.hr_timeout_hours = int(data.get("hr_timeout_hours", 48))
            workflow.send_reminder_before_hours = int(
                data.get("send_reminder_before_hours", 2)
            )
            workflow.max_reminders = int(data.get("max_reminders", 3))
            workflow.is_active = data.get("is_active") == "on"
            workflow.save()

            messages.success(
                request,
                f"Workflow đã được cập nhật thành công cho {workflow.department.full_name} - {workflow.absence_type.name}",
            )
            return redirect("absence:workflow_config")

        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật workflow: {str(e)}")

    departments = Department.objects.select_related("office").all()
    absence_types = AbsenceType.objects.all()

    return render(
        request,
        "absence/workflow_update.html",
        {
            "workflow": workflow,
            "departments": departments,
            "absence_types": absence_types,
        },
    )
