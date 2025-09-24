"""
Management command để migrate cấu trúc phòng ban từ 1 cấp sang 2 cấp
"""
from django.core.management.base import BaseCommand
from apps.users.models import Office, Department, User


class Command(BaseCommand):
    help = 'Migrate department structure from single level to two levels (Office -> Department)'

    def handle(self, *args, **options):
        self.stdout.write('Starting department structure migration...')
        
        # Tạo các văn phòng mẫu
        offices_data = [
            {'name': 'VP Hà Nội', 'description': 'Văn phòng tại Hà Nội'},
            {'name': 'VP Thái Nguyên', 'description': 'Văn phòng tại Thái Nguyên'},
            {'name': 'VP Tuyên Quang', 'description': 'Văn phòng tại Tuyên Quang'},
            {'name': 'VP Hồ Chí Minh', 'description': 'Văn phòng tại TP. Hồ Chí Minh'},
            {'name': 'VP Đà Nẵng', 'description': 'Văn phòng tại Đà Nẵng'},
        ]
        
        offices = {}
        for office_data in offices_data:
            office, created = Office.objects.get_or_create(
                name=office_data['name'],
                defaults={'description': office_data['description']}
            )
            offices[office_data['name']] = office
            if created:
                self.stdout.write(f'Created office: {office.name}')
        
        # Tạo các phòng ban mẫu cho từng văn phòng
        departments_data = [
            # VP Hà Nội
            {'name': 'Phòng Kinh doanh', 'office': 'VP Hà Nội', 'description': 'Phòng kinh doanh tại Hà Nội'},
            {'name': 'Phòng Kỹ thuật', 'office': 'VP Hà Nội', 'description': 'Phòng kỹ thuật tại Hà Nội'},
            {'name': 'Phòng Nhân sự', 'office': 'VP Hà Nội', 'description': 'Phòng nhân sự tại Hà Nội'},
            {'name': 'Phòng Marketing', 'office': 'VP Hà Nội', 'description': 'Phòng marketing tại Hà Nội'},
            {'name': 'Phòng Tài chính', 'office': 'VP Hà Nội', 'description': 'Phòng tài chính tại Hà Nội'},
            
            # VP Thái Nguyên
            {'name': 'Phòng Kinh doanh', 'office': 'VP Thái Nguyên', 'description': 'Phòng kinh doanh tại Thái Nguyên'},
            {'name': 'Phòng Kỹ thuật', 'office': 'VP Thái Nguyên', 'description': 'Phòng kỹ thuật tại Thái Nguyên'},
            {'name': 'Phòng Nhân sự', 'office': 'VP Thái Nguyên', 'description': 'Phòng nhân sự tại Thái Nguyên'},
            {'name': 'Phòng Marketing', 'office': 'VP Thái Nguyên', 'description': 'Phòng marketing tại Thái Nguyên'},
            
            # VP Tuyên Quang
            {'name': 'Phòng Kinh doanh', 'office': 'VP Tuyên Quang', 'description': 'Phòng kinh doanh tại Tuyên Quang'},
            {'name': 'Phòng Kỹ thuật', 'office': 'VP Tuyên Quang', 'description': 'Phòng kỹ thuật tại Tuyên Quang'},
            {'name': 'Phòng Nhân sự', 'office': 'VP Tuyên Quang', 'description': 'Phòng nhân sự tại Tuyên Quang'},
            
            # VP Hồ Chí Minh
            {'name': 'Phòng Kinh doanh', 'office': 'VP Hồ Chí Minh', 'description': 'Phòng kinh doanh tại TP.HCM'},
            {'name': 'Phòng Kỹ thuật', 'office': 'VP Hồ Chí Minh', 'description': 'Phòng kỹ thuật tại TP.HCM'},
            {'name': 'Phòng Marketing', 'office': 'VP Hồ Chí Minh', 'description': 'Phòng marketing tại TP.HCM'},
            {'name': 'Phòng Tài chính', 'office': 'VP Hồ Chí Minh', 'description': 'Phòng tài chính tại TP.HCM'},
            
            # VP Đà Nẵng
            {'name': 'Phòng Kinh doanh', 'office': 'VP Đà Nẵng', 'description': 'Phòng kinh doanh tại Đà Nẵng'},
            {'name': 'Phòng Kỹ thuật', 'office': 'VP Đà Nẵng', 'description': 'Phòng kỹ thuật tại Đà Nẵng'},
            {'name': 'Phòng Marketing', 'office': 'VP Đà Nẵng', 'description': 'Phòng marketing tại Đà Nẵng'},
        ]
        
        # Xóa tất cả phòng ban cũ
        Department.objects.all().delete()
        self.stdout.write('Deleted old departments')
        
        # Tạo phòng ban mới
        for dept_data in departments_data:
            office = offices[dept_data['office']]
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                office=office,
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'Created department: {department.full_name}')
        
        # Cập nhật user để gán vào phòng ban mới
        self.stdout.write('Updating user departments...')
        users = User.objects.all()
        departments = list(Department.objects.all())
        
        for i, user in enumerate(users):
            if departments:
                # Phân bổ đều user vào các phòng ban
                department = departments[i % len(departments)]
                user.department = department
                user.save()
                self.stdout.write(f'Updated user {user.username} to department {department.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully migrated department structure!\n'
                f'Created {len(offices)} offices and {len(departments)} departments'
            )
        )
