from django.core.management.base import BaseCommand
from checkin.models import User, UserRole

class Command(BaseCommand):
    help = 'Tạo users mẫu với các vai trò khác nhau'

    def handle(self, *args, **options):
        # Tạo Manager
        manager, created = User.objects.get_or_create(
            email='manager@nov-reco.com',
            defaults={
                'username': 'manager@nov-reco.com',
                'first_name': 'Nguyễn',
                'last_name': 'Quản Lý',
                'role': UserRole.MANAGER,
                'phone': '0901234567',
                'department': 'Quản lý',
                'employee_id': 'MGR001'
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()

        # Tạo Employee 1
        employee1, created = User.objects.get_or_create(
            email='employee1@nov-reco.com',
            defaults={
                'username': 'employee1@nov-reco.com',
                'first_name': 'Trần',
                'last_name': 'Nhân Viên',
                'role': UserRole.EMPLOYEE,
                'phone': '0901234568',
                'department': 'Kỹ thuật',
                'employee_id': 'EMP001'
            }
        )
        if created:
            employee1.set_password('emp123')
            employee1.save()

        # Tạo Employee 2
        employee2, created = User.objects.get_or_create(
            email='employee2@nov-reco.com',
            defaults={
                'username': 'employee2@nov-reco.com',
                'first_name': 'Lê',
                'last_name': 'Công Nhân',
                'role': UserRole.EMPLOYEE,
                'phone': '0901234569',
                'department': 'Kinh doanh',
                'employee_id': 'EMP002'
            }
        )
        if created:
            employee2.set_password('emp123')
            employee2.save()

        self.stdout.write(
            self.style.SUCCESS('✅ Đã tạo users mẫu thành công!')
        )
        self.stdout.write('👑 Admin: admin@nov-reco.com / admin123')
        self.stdout.write('👨‍💼 Manager: manager@nov-reco.com / manager123')
        self.stdout.write('👤 Employee 1: employee1@nov-reco.com / emp123')
        self.stdout.write('👤 Employee 2: employee2@nov-reco.com / emp123')

