from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.users.models import Department, Office

User = get_user_model()


class AbsenceType(models.Model):
    """Loại vắng mặt"""

    name = models.CharField(max_length=100, help_text="Tên loại vắng mặt")
    code = models.CharField(max_length=20, unique=True, help_text="Mã loại vắng mặt")
    description = models.TextField(blank=True, help_text="Mô tả")
    requires_approval = models.BooleanField(default=True, help_text="Cần phê duyệt")
    max_days_per_year = models.IntegerField(
        null=True, blank=True, help_text="Số ngày tối đa/năm"
    )
    is_active = models.BooleanField(default=True, help_text="Đang hoạt động")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Màu hiển thị")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Loại vắng mặt"
        verbose_name_plural = "Loại vắng mặt"

    def __str__(self):
        return self.name


class ApprovalWorkflow(models.Model):
    """Cấu hình workflow phê duyệt theo phòng ban"""

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, help_text="Phòng ban"
    )
    absence_type = models.ForeignKey(
        AbsenceType, on_delete=models.CASCADE, help_text="Loại vắng mặt"
    )

    # Cấu hình workflow
    requires_department_manager = models.BooleanField(
        default=True, help_text="Cần Trưởng phòng"
    )
    requires_department_deputy = models.BooleanField(
        default=False, help_text="Cần Phó phòng"
    )
    requires_office_director = models.BooleanField(
        default=False, help_text="Cần Giám đốc VP"
    )
    requires_office_deputy = models.BooleanField(
        default=False, help_text="Cần Phó GĐ VP"
    )
    requires_hr_approval = models.BooleanField(default=True, help_text="Cần HR")

    # Thứ tự ưu tiên
    department_manager_priority = models.IntegerField(
        default=1, help_text="Ưu tiên Trưởng phòng"
    )
    department_deputy_priority = models.IntegerField(
        default=2, help_text="Ưu tiên Phó phòng"
    )
    office_director_priority = models.IntegerField(
        default=3, help_text="Ưu tiên Giám đốc VP"
    )
    office_deputy_priority = models.IntegerField(
        default=4, help_text="Ưu tiên Phó GĐ VP"
    )

    # Timeout settings
    department_manager_timeout_hours = models.IntegerField(
        default=24, help_text="Timeout Trưởng phòng (giờ)"
    )
    department_deputy_timeout_hours = models.IntegerField(
        default=24, help_text="Timeout Phó phòng (giờ)"
    )
    office_director_timeout_hours = models.IntegerField(
        default=48, help_text="Timeout Giám đốc VP (giờ)"
    )
    office_deputy_timeout_hours = models.IntegerField(
        default=48, help_text="Timeout Phó GĐ VP (giờ)"
    )
    hr_timeout_hours = models.IntegerField(default=24, help_text="Timeout HR (giờ)")

    # Reminder settings
    send_reminder_before_hours = models.IntegerField(
        default=2, help_text="Gửi nhắc nhở trước (giờ)"
    )
    max_reminders = models.IntegerField(default=3, help_text="Số lần nhắc nhở tối đa")

    is_active = models.BooleanField(default=True, help_text="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["department", "absence_type"]
        verbose_name = "Workflow phê duyệt"
        verbose_name_plural = "Workflow phê duyệt"

    def __str__(self):
        return f"{self.department.full_name} - {self.absence_type.name}"


class AbsenceRequest(models.Model):
    """Đơn xin vắng mặt"""

    STATUS_CHOICES = [
        ("pending", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("cancelled", "Đã hủy"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Người tạo đơn")
    absence_type = models.ForeignKey(
        AbsenceType, on_delete=models.CASCADE, help_text="Loại vắng mặt"
    )
    workflow = models.ForeignKey(
        ApprovalWorkflow, on_delete=models.CASCADE, help_text="Workflow"
    )

    # Thông tin đơn
    start_date = models.DateField(help_text="Ngày bắt đầu")
    end_date = models.DateField(help_text="Ngày kết thúc")
    start_time = models.TimeField(null=True, blank=True, help_text="Giờ bắt đầu")
    end_time = models.TimeField(null=True, blank=True, help_text="Giờ kết thúc")
    total_days = models.DecimalField(
        max_digits=4, decimal_places=1, help_text="Tổng số ngày"
    )
    reason = models.TextField(help_text="Lý do")
    attachment = models.FileField(
        upload_to="absence_attachments/",
        null=True,
        blank=True,
        help_text="File đính kèm",
    )

    # Workflow tracking
    current_approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pending_approvals",
        help_text="Người phê duyệt hiện tại",
    )
    approval_level = models.CharField(
        max_length=50, default="department_manager", help_text="Cấp phê duyệt hiện tại"
    )

    # Phê duyệt cuối cùng
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", help_text="Trạng thái"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_absences",
        help_text="Người phê duyệt cuối cùng",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="Thời gian phê duyệt"
    )
    rejection_reason = models.TextField(blank=True, help_text="Lý do từ chối")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Đơn vắng mặt"
        verbose_name_plural = "Đơn vắng mặt"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.absence_type.name} ({self.start_date} - {self.end_date})"

    @property
    def status_display(self):
        """Hiển thị trạng thái"""
        status_map = {
            "pending": "Chờ duyệt",
            "approved": "Đã duyệt",
            "rejected": "Từ chối",
            "cancelled": "Đã hủy",
        }
        return status_map.get(self.status, self.status)

    @property
    def is_overdue(self):
        """Kiểm tra đơn có quá hạn không"""
        if self.status != "pending":
            return False

        # Kiểm tra timeout dựa trên approval level
        timeout_hours = self._get_timeout_hours()
        if timeout_hours:
            deadline = self.created_at + timezone.timedelta(hours=timeout_hours)
            return timezone.now() > deadline

        return False

    def _get_timeout_hours(self):
        """Lấy số giờ timeout cho cấp phê duyệt hiện tại"""
        timeout_map = {
            "department_manager": self.workflow.department_manager_timeout_hours,
            "department_deputy": self.workflow.department_deputy_timeout_hours,
            "office_director": self.workflow.office_director_timeout_hours,
            "office_deputy": self.workflow.office_deputy_timeout_hours,
            "hr": self.workflow.hr_timeout_hours,
        }
        return timeout_map.get(self.approval_level)


class ApprovalHistory(models.Model):
    """Lịch sử phê duyệt"""

    ACTION_CHOICES = [
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("forwarded", "Chuyển tiếp"),
    ]

    absence_request = models.ForeignKey(
        AbsenceRequest, on_delete=models.CASCADE, help_text="Đơn vắng mặt"
    )
    approver = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Người phê duyệt"
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, help_text="Hành động"
    )
    level = models.CharField(max_length=50, help_text="Cấp phê duyệt")
    comment = models.TextField(blank=True, help_text="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lịch sử phê duyệt"
        verbose_name_plural = "Lịch sử phê duyệt"

    def __str__(self):
        return f"{self.approver.get_full_name()} - {self.get_action_display()} - {self.absence_request}"
