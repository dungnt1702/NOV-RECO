from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User


class Command(BaseCommand):
    help = 'Create sample users for each group'

    def handle(self, *args, **options):
        # Dữ liệu users mẫu
        sample_users = [
            {
                'username': 'superadmin',
                'email': 'superadmin@reco.local',
                'password': 'admin123',
                'first_name': 'Super',
                'last_name': 'Admin',
                'employee_id': 'SA001',
                'group': 'Super Admin',
                'role': 'admin',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'quanly',
                'email': 'quanly@reco.local',
                'password': 'quanly123',
                'first_name': 'Nguyễn',
                'last_name': 'Quản Lý',
                'employee_id': 'QL001',
                'group': 'Quản lý',
                'role': 'manager',
                'is_staff': True,
            },
            {
                'username': 'thuky',
                'email': 'thuky@reco.local',
                'password': 'thuky123',
                'first_name': 'Trần',
                'last_name': 'Thư Ký',
                'employee_id': 'TK001',
                'group': 'Thư ký',
                'role': 'employee',
                'is_staff': True,
            },
            {
                'username': 'nhanvien1',
                'email': 'nhanvien1@reco.local',
                'password': 'nhanvien123',
                'first_name': 'Lê',
                'last_name': 'Nhân Viên',
                'employee_id': 'NV001',
                'group': 'Nhân viên',
                'role': 'employee',
                'is_staff': False,
            },
            {
                'username': 'nhanvien2',
                'email': 'nhanvien2@reco.local',
                'password': 'nhanvien123',
                'first_name': 'Phạm',
                'last_name': 'Văn Bình',
                'employee_id': 'NV002',
                'group': 'Nhân viên',
                'role': 'employee',
                'is_staff': False,
            },
        ]

        for user_data in sample_users:
            username = user_data['username']
            group_name = user_data.pop('group')
            role = user_data.pop('role')
            
            # Kiểm tra user đã tồn tại chưa
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists')
                )
                continue
            
            # Tạo user mới
            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    employee_id=user_data['employee_id'],
                    role=role,
                )
                
                # Set superuser và staff status
                if user_data.get('is_superuser'):
                    user.is_superuser = True
                if user_data.get('is_staff'):
                    user.is_staff = True
                
                user.save()
                
                # Thêm vào group
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created user: {username} ({group_name})'
                        )
                    )
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Group {group_name} does not exist')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user {username}: {str(e)}')
                )

        # Hiển thị thông tin đăng nhập
        self.stdout.write(
            self.style.SUCCESS('\n=== THÔNG TIN ĐĂNG NHẬP ===')
        )
        self.stdout.write('Super Admin: superadmin / admin123')
        self.stdout.write('Quản lý: quanly / quanly123')
        self.stdout.write('Thư ký: thuky / thuky123')
        self.stdout.write('Nhân viên 1: nhanvien1 / nhanvien123')
        self.stdout.write('Nhân viên 2: nhanvien2 / nhanvien123')
        self.stdout.write(
            self.style.SUCCESS('Sample users created successfully!')
        )