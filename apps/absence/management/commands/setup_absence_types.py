from django.core.management.base import BaseCommand

from apps.absence.models import AbsenceType, ApprovalWorkflow
from apps.users.models import Department


class Command(BaseCommand):
    help = "Thiết lập các loại vắng mặt và workflow mặc định"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chạy thử không thực hiện thay đổi",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("=== DRY RUN MODE - Không thực hiện thay đổi ===")
            )

        # Tạo các loại vắng mặt
        self.create_absence_types(dry_run)

        # Tạo workflow mặc định
        self.create_default_workflows(dry_run)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("Hoàn thành thiết lập loại vắng mặt và workflow!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run hoàn thành. Chạy lại không có --dry-run để thực hiện."
                )
            )

    def create_absence_types(self, dry_run):
        """Tạo các loại vắng mặt"""
        self.stdout.write("\n=== TẠO LOẠI VẮNG MẶT ===")

        absence_types = [
            {
                "name": "Nghỉ phép năm",
                "code": "ANNUAL_LEAVE",
                "description": "Nghỉ phép năm theo quy định",
                "requires_approval": True,
                "max_days_per_year": 12,
                "color": "#10B981",
            },
            {
                "name": "Nghỉ ốm",
                "code": "SICK_LEAVE",
                "description": "Nghỉ ốm, nghỉ khám bệnh",
                "requires_approval": True,
                "max_days_per_year": 30,
                "color": "#F59E0B",
            },
            {
                "name": "Nghỉ việc riêng",
                "code": "PERSONAL_LEAVE",
                "description": "Nghỉ việc riêng, nghỉ không lương",
                "requires_approval": True,
                "max_days_per_year": 5,
                "color": "#8B5CF6",
            },
            {
                "name": "Nghỉ thai sản",
                "code": "MATERNITY_LEAVE",
                "description": "Nghỉ thai sản theo quy định",
                "requires_approval": True,
                "max_days_per_year": 180,
                "color": "#EC4899",
            },
            {
                "name": "Nghỉ tang",
                "code": "BEREAVEMENT_LEAVE",
                "description": "Nghỉ tang gia đình",
                "requires_approval": True,
                "max_days_per_year": 3,
                "color": "#6B7280",
            },
            {
                "name": "Nghỉ học tập",
                "code": "STUDY_LEAVE",
                "description": "Nghỉ để học tập, thi cử",
                "requires_approval": True,
                "max_days_per_year": 10,
                "color": "#3B82F6",
            },
            {
                "name": "Nghỉ công tác",
                "code": "BUSINESS_TRIP",
                "description": "Nghỉ để đi công tác",
                "requires_approval": True,
                "max_days_per_year": None,
                "color": "#06B6D4",
            },
            {
                "name": "Nghỉ nửa ngày",
                "code": "HALF_DAY",
                "description": "Nghỉ nửa ngày",
                "requires_approval": False,
                "max_days_per_year": None,
                "color": "#84CC16",
            },
        ]

        for absence_data in absence_types:
            absence_type, created = AbsenceType.objects.get_or_create(
                code=absence_data["code"], defaults=absence_data
            )

            if created:
                self.stdout.write(f"  ✓ Tạo mới: {absence_type.name}")
            else:
                self.stdout.write(f"  - Đã tồn tại: {absence_type.name}")

            if not dry_run and created:
                # Không cần save vì đã tạo mới
                pass

    def create_default_workflows(self, dry_run):
        """Tạo workflow mặc định cho các phòng ban"""
        self.stdout.write("\n=== TẠO WORKFLOW MẶC ĐỊNH ===")

        departments = Department.objects.all()
        absence_types = AbsenceType.objects.all()

        workflow_count = 0

        for department in departments:
            for absence_type in absence_types:
                workflow, created = ApprovalWorkflow.objects.get_or_create(
                    department=department,
                    absence_type=absence_type,
                    defaults={
                        "requires_department_manager": True,
                        "requires_department_deputy": False,
                        "requires_office_director": False,
                        "requires_office_deputy": False,
                        "requires_hr_approval": True,
                        "department_manager_priority": 1,
                        "department_deputy_priority": 2,
                        "office_director_priority": 3,
                        "office_deputy_priority": 4,
                        "department_manager_timeout_hours": 24,
                        "department_deputy_timeout_hours": 24,
                        "office_director_timeout_hours": 48,
                        "office_deputy_timeout_hours": 48,
                        "hr_timeout_hours": 24,
                        "send_reminder_before_hours": 2,
                        "max_reminders": 3,
                        "is_active": True,
                    },
                )

                if created:
                    workflow_count += 1
                    self.stdout.write(
                        f"  ✓ Tạo workflow: {department.full_name} - {absence_type.name}"
                    )

        self.stdout.write(f"\nTổng cộng tạo {workflow_count} workflow mới")

        # Cập nhật workflow cho các loại vắng mặt đặc biệt
        self.update_special_workflows(dry_run)

    def update_special_workflows(self, dry_run):
        """Cập nhật workflow cho các loại vắng mặt đặc biệt"""
        self.stdout.write("\n=== CẬP NHẬT WORKFLOW ĐẶC BIỆT ===")

        # Nghỉ thai sản cần phê duyệt từ HR
        maternity_type = AbsenceType.objects.filter(code="MATERNITY_LEAVE").first()
        if maternity_type:
            workflows = ApprovalWorkflow.objects.filter(absence_type=maternity_type)
            for workflow in workflows:
                workflow.requires_hr_approval = True
                workflow.hr_timeout_hours = 48  # Thời gian dài hơn cho HR
                if not dry_run:
                    workflow.save()
                self.stdout.write(
                    f"  ✓ Cập nhật workflow nghỉ thai sản: {workflow.department.full_name}"
                )

        # Nghỉ nửa ngày không cần phê duyệt
        half_day_type = AbsenceType.objects.filter(code="HALF_DAY").first()
        if half_day_type:
            workflows = ApprovalWorkflow.objects.filter(absence_type=half_day_type)
            for workflow in workflows:
                workflow.requires_department_manager = False
                workflow.requires_hr_approval = False
                if not dry_run:
                    workflow.save()
                self.stdout.write(
                    f"  ✓ Cập nhật workflow nghỉ nửa ngày: {workflow.department.full_name}"
                )

        # Nghỉ công tác cần phê duyệt từ Giám đốc VP
        business_trip_type = AbsenceType.objects.filter(code="BUSINESS_TRIP").first()
        if business_trip_type:
            workflows = ApprovalWorkflow.objects.filter(absence_type=business_trip_type)
            for workflow in workflows:
                workflow.requires_office_director = True
                workflow.office_director_timeout_hours = 72  # Thời gian dài hơn
                if not dry_run:
                    workflow.save()
                self.stdout.write(
                    f"  ✓ Cập nhật workflow nghỉ công tác: {workflow.department.full_name}"
                )
