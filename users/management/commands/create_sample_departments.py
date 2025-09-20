from django.core.management.base import BaseCommand
from users.models import Department, User


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho phòng ban'

    def handle(self, *args, **options):
        # Tạo các phòng ban mẫu
        departments_data = [
            {
                'name': 'Phòng Kế toán',
                'description': 'Quản lý tài chính, kế toán và báo cáo tài chính của công ty'
            },
            {
                'name': 'Phòng Nhân sự',
                'description': 'Quản lý nhân sự, tuyển dụng, đào tạo và phúc lợi nhân viên'
            },
            {
                'name': 'Phòng Kỹ thuật',
                'description': 'Phát triển phần mềm, bảo trì hệ thống và hỗ trợ kỹ thuật'
            },
            {
                'name': 'Phòng Kinh doanh',
                'description': 'Phát triển kinh doanh, bán hàng và quan hệ khách hàng'
            },
            {
                'name': 'Phòng Marketing',
                'description': 'Marketing, quảng cáo, truyền thông và phát triển thương hiệu'
            },
            {
                'name': 'Phòng Hành chính',
                'description': 'Hành chính, quản lý văn phòng và hỗ trợ hoạt động'
            },
            {
                'name': 'Phòng Chất lượng',
                'description': 'Đảm bảo chất lượng sản phẩm và dịch vụ'
            },
            {
                'name': 'Phòng Pháp chế',
                'description': 'Tư vấn pháp lý và tuân thủ quy định'
            }
        ]

        created_count = 0
        updated_count = 0

        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Đã tạo phòng ban: {department.name}")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Phòng ban đã tồn tại: {department.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nHoàn thành! Đã tạo {created_count} phòng ban mới, "
                f"{updated_count} phòng ban đã tồn tại."
            )
        )

        # Hiển thị danh sách phòng ban
        self.stdout.write("\nDanh sách phòng ban hiện có:")
        departments = Department.objects.all().order_by('name')
        for dept in departments:
            employee_count = dept.employee_count
            self.stdout.write(f"- {dept.name} ({employee_count} nhân viên)")
