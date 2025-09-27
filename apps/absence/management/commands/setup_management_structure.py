from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.users.models import Department, Office

User = get_user_model()


class Command(BaseCommand):
    help = "Thiết lập cấu trúc quản lý cho văn phòng và phòng ban"

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

        # Lấy danh sách users có role admin hoặc manager
        admin_users = User.objects.filter(role__in=["admin", "manager"], is_active=True)

        if not admin_users.exists():
            self.stdout.write(
                self.style.ERROR("Không tìm thấy user nào có role admin hoặc manager!")
            )
            return

        self.stdout.write(f"Tìm thấy {admin_users.count()} users có thể làm quản lý")

        # Thiết lập quản lý cho các văn phòng
        self.setup_office_management(admin_users, dry_run)

        # Thiết lập quản lý cho các phòng ban
        self.setup_department_management(admin_users, dry_run)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("Hoàn thành thiết lập cấu trúc quản lý!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Dry run hoàn thành. Chạy lại không có --dry-run để thực hiện."
                )
            )

    def setup_office_management(self, admin_users, dry_run):
        """Thiết lập quản lý cho văn phòng"""
        self.stdout.write("\n=== THIẾT LẬP QUẢN LÝ VĂN PHÒNG ===")

        offices = Office.objects.all()
        admin_list = list(admin_users)
        admin_index = 0

        for office in offices:
            self.stdout.write(f"\nVăn phòng: {office.name}")

            # Gán Giám đốc
            if not office.director and admin_index < len(admin_list):
                director = admin_list[admin_index]
                self.stdout.write(f"  → Gán Giám đốc: {director.get_full_name()}")
                if not dry_run:
                    office.director = director
                    office.save()
                admin_index += 1

            # Gán Phó Giám đốc
            if not office.deputy_director and admin_index < len(admin_list):
                deputy_director = admin_list[admin_index]
                self.stdout.write(f"  → Gán Phó GĐ: {deputy_director.get_full_name()}")
                if not dry_run:
                    office.deputy_director = deputy_director
                    office.save()
                admin_index += 1

            if admin_index >= len(admin_list):
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Hết users có thể làm quản lý!")
                )
                break

    def setup_department_management(self, admin_users, dry_run):
        """Thiết lập quản lý cho phòng ban"""
        self.stdout.write("\n=== THIẾT LẬP QUẢN LÝ PHÒNG BAN ===")

        departments = Department.objects.select_related("office").all()
        admin_list = list(admin_users)
        admin_index = 0

        for department in departments:
            self.stdout.write(f"\nPhòng ban: {department.full_name}")

            # Gán Trưởng phòng
            if not department.manager and admin_index < len(admin_list):
                manager = admin_list[admin_index]
                self.stdout.write(f"  → Gán Trưởng phòng: {manager.get_full_name()}")
                if not dry_run:
                    department.manager = manager
                    department.save()
                admin_index += 1

            # Gán Phó phòng
            if not department.deputy_manager and admin_index < len(admin_list):
                deputy_manager = admin_list[admin_index]
                self.stdout.write(
                    f"  → Gán Phó phòng: {deputy_manager.get_full_name()}"
                )
                if not dry_run:
                    department.deputy_manager = deputy_manager
                    department.save()
                admin_index += 1

            if admin_index >= len(admin_list):
                self.stdout.write(
                    self.style.WARNING("  ⚠️  Hết users có thể làm quản lý!")
                )
                break

    def get_management_summary(self):
        """Lấy tổng kết cấu trúc quản lý"""
        offices_with_director = Office.objects.filter(director__isnull=False).count()
        offices_with_deputy = Office.objects.filter(
            deputy_director__isnull=False
        ).count()
        departments_with_manager = Department.objects.filter(
            manager__isnull=False
        ).count()
        departments_with_deputy = Department.objects.filter(
            deputy_manager__isnull=False
        ).count()

        return {
            "offices_with_director": offices_with_director,
            "offices_with_deputy": offices_with_deputy,
            "departments_with_manager": departments_with_manager,
            "departments_with_deputy": departments_with_deputy,
        }
