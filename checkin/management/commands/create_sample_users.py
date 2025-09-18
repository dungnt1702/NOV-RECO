from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import User, UserRole

class Command(BaseCommand):
    help = 'Tạo dữ liệu người dùng mẫu'

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu người dùng mẫu...')
        
        # Tạo Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@nhaongay.vn',
                'first_name': 'Quản trị',
                'last_name': 'Viên',
                'role': UserRole.ADMIN,
                'phone': '0123456789',
                'department': 'IT',
                'employee_id': 'ADM001',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Đã tạo Admin: {admin.username} (admin123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Admin đã tồn tại: {admin.username}')
            )

        # Tạo Manager
        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@nhaongay.vn',
                'first_name': 'Quản lý',
                'last_name': 'Viên',
                'role': UserRole.MANAGER,
                'phone': '0123456790',
                'department': 'Quản lý',
                'employee_id': 'MGR001',
                'is_active': True,
                'is_staff': True,
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Đã tạo Manager: {manager.username} (manager123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Manager đã tồn tại: {manager.username}')
            )

        # Tạo 5 Employees
        employees_data = [
            {
                'username': 'employee1',
                'email': 'nhanvien1@nhaongay.vn',
                'first_name': 'Nguyễn',
                'last_name': 'Văn A',
                'phone': '0123456791',
                'department': 'Kinh doanh',
                'employee_id': 'EMP001',
            },
            {
                'username': 'employee2',
                'email': 'nhanvien2@nhaongay.vn',
                'first_name': 'Trần',
                'last_name': 'Thị B',
                'phone': '0123456792',
                'department': 'Marketing',
                'employee_id': 'EMP002',
            },
            {
                'username': 'employee3',
                'email': 'nhanvien3@nhaongay.vn',
                'first_name': 'Lê',
                'last_name': 'Văn C',
                'phone': '0123456793',
                'department': 'Kỹ thuật',
                'employee_id': 'EMP003',
            },
            {
                'username': 'employee4',
                'email': 'nhanvien4@nhaongay.vn',
                'first_name': 'Phạm',
                'last_name': 'Thị D',
                'phone': '0123456794',
                'department': 'Hành chính',
                'employee_id': 'EMP004',
            },
            {
                'username': 'employee5',
                'email': 'nhanvien5@nhaongay.vn',
                'first_name': 'Hoàng',
                'last_name': 'Văn E',
                'phone': '0123456795',
                'department': 'Tài chính',
                'employee_id': 'EMP005',
            },
        ]

        for emp_data in employees_data:
            employee, created = User.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'email': emp_data['email'],
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'role': UserRole.EMPLOYEE,
                    'phone': emp_data['phone'],
                    'department': emp_data['department'],
                    'employee_id': emp_data['employee_id'],
                    'is_active': True,
                }
            )
            if created:
                employee.set_password('employee123')
                employee.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Đã tạo Employee: {employee.username} (employee123)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Employee đã tồn tại: {employee.username}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Hoàn thành tạo dữ liệu người dùng mẫu!')
        )
        self.stdout.write('\n📋 Thông tin đăng nhập:')
        self.stdout.write('👑 Admin: admin / admin123')
        self.stdout.write('👨‍💼 Manager: manager / manager123')
        self.stdout.write('👷 Employees: employee1-5 / employee123')