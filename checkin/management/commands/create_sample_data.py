from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Department, UserRole
from checkin.models import Area, Checkin
from django.utils import timezone
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho tất cả modules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Xóa dữ liệu cũ trước khi tạo mới',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Xóa dữ liệu cũ...')
            Checkin.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Department.objects.all().delete()
            Area.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Đã xóa dữ liệu cũ'))

        self.stdout.write('🚀 Bắt đầu tạo dữ liệu mẫu...')

        # 1. Tạo Departments
        self.create_departments()

        # 2. Tạo Users
        self.create_users()

        # 3. Tạo Areas
        self.create_areas()

        # 4. Tạo Check-ins
        self.create_checkins()

        self.stdout.write(self.style.SUCCESS('✅ Hoàn thành tạo dữ liệu mẫu!'))

    def create_departments(self):
        """Tạo các phòng ban mẫu"""
        self.stdout.write('📁 Tạo phòng ban...')
        
        departments_data = [
            {
                'name': 'Phòng Công nghệ thông tin',
                'description': 'Phụ trách phát triển và bảo trì hệ thống công nghệ thông tin'
            },
            {
                'name': 'Phòng Nhân sự',
                'description': 'Quản lý nhân sự, tuyển dụng và đào tạo nhân viên'
            },
            {
                'name': 'Phòng Kế toán',
                'description': 'Quản lý tài chính, kế toán và báo cáo tài chính'
            },
            {
                'name': 'Phòng Kinh doanh',
                'description': 'Phát triển kinh doanh, marketing và bán hàng'
            },
            {
                'name': 'Phòng Sản xuất',
                'description': 'Quản lý sản xuất, chất lượng và logistics'
            },
            {
                'name': 'Phòng Hành chính',
                'description': 'Quản lý hành chính, văn phòng và hỗ trợ'
            }
        ]

        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'  ✅ Tạo phòng ban: {dept.name}')

        self.departments = departments
        return departments

    def create_users(self):
        """Tạo người dùng mẫu"""
        self.stdout.write('👥 Tạo người dùng...')

        # Lấy admin hiện tại để làm manager của một số phòng ban
        admin = User.objects.filter(is_superuser=True).first()
        
        users_data = [
            # Managers
            {
                'username': 'manager_it',
                'email': 'manager.it@company.com',
                'first_name': 'Nguyễn',
                'last_name': 'Văn A',
                'role': UserRole.MANAGER,
                'department': self.departments[0],  # IT
                'employee_id': 'MNG001',
                'is_active': True
            },
            {
                'username': 'manager_hr',
                'email': 'manager.hr@company.com',
                'first_name': 'Trần',
                'last_name': 'Thị B',
                'role': UserRole.MANAGER,
                'department': self.departments[1],  # HR
                'employee_id': 'MNG002',
                'is_active': True
            },
            {
                'username': 'manager_finance',
                'email': 'manager.finance@company.com',
                'first_name': 'Lê',
                'last_name': 'Văn C',
                'role': UserRole.MANAGER,
                'department': self.departments[2],  # Finance
                'employee_id': 'MNG003',
                'is_active': True
            },

            # HCNS
            {
                'username': 'hcns_main',
                'email': 'hcns.main@company.com',
                'first_name': 'Phạm',
                'last_name': 'Thị D',
                'role': UserRole.HCNS,
                'department': self.departments[1],  # HR
                'employee_id': 'HCNS001',
                'is_active': True
            },
            {
                'username': 'hcns_recruit',
                'email': 'hcns.recruit@company.com',
                'first_name': 'Hoàng',
                'last_name': 'Văn E',
                'role': UserRole.HCNS,
                'department': self.departments[1],  # HR
                'employee_id': 'HCNS002',
                'is_active': True
            },

            # Employees
            {
                'username': 'dev_001',
                'email': 'dev001@company.com',
                'first_name': 'Nguyễn',
                'last_name': 'Văn F',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[0],  # IT
                'employee_id': 'EMP001',
                'is_active': True
            },
            {
                'username': 'dev_002',
                'email': 'dev002@company.com',
                'first_name': 'Trần',
                'last_name': 'Thị G',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[0],  # IT
                'employee_id': 'EMP002',
                'is_active': True
            },
            {
                'username': 'accountant_001',
                'email': 'accountant001@company.com',
                'first_name': 'Lê',
                'last_name': 'Thị H',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[2],  # Finance
                'employee_id': 'EMP003',
                'is_active': True
            },
            {
                'username': 'sales_001',
                'email': 'sales001@company.com',
                'first_name': 'Phạm',
                'last_name': 'Văn I',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[3],  # Sales
                'employee_id': 'EMP004',
                'is_active': True
            },
            {
                'username': 'production_001',
                'email': 'production001@company.com',
                'first_name': 'Hoàng',
                'last_name': 'Thị J',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[4],  # Production
                'employee_id': 'EMP005',
                'is_active': True
            },
            {
                'username': 'admin_001',
                'email': 'admin001@company.com',
                'first_name': 'Vũ',
                'last_name': 'Văn K',
                'role': UserRole.EMPLOYEE,
                'department': self.departments[5],  # Admin
                'employee_id': 'EMP006',
                'is_active': True
            }
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'department': user_data['department'],
                    'employee_id': user_data['employee_id'],
                    'is_active': user_data['is_active']
                }
            )
            
            if created:
                # Set password mặc định
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✅ Tạo user: {user.username} ({user.get_role_display()})')
            else:
                self.stdout.write(f'  ⚠️  User đã tồn tại: {user.username}')
            
            users.append(user)

        # Cập nhật manager cho departments
        self.departments[0].manager = users[0]  # IT manager
        self.departments[0].save()
        self.departments[1].manager = users[1]  # HR manager
        self.departments[1].save()
        self.departments[2].manager = users[2]  # Finance manager
        self.departments[2].save()

        self.users = users
        return users

    def create_areas(self):
        """Tạo khu vực mẫu"""
        self.stdout.write('📍 Tạo khu vực...')

        # Lấy admin để làm created_by
        admin = User.objects.filter(is_superuser=True).first()
        
        areas_data = [
            {
                'name': 'Văn phòng chính',
                'description': 'Tòa nhà văn phòng chính của công ty',
                'lat': 21.0285,
                'lng': 105.8542,
                'radius_m': 100
            },
            {
                'name': 'Nhà máy sản xuất',
                'description': 'Khu vực nhà máy sản xuất chính',
                'lat': 21.0385,
                'lng': 105.8642,
                'radius_m': 150
            },
            {
                'name': 'Kho hàng',
                'description': 'Khu vực kho hàng và logistics',
                'lat': 21.0485,
                'lng': 105.8742,
                'radius_m': 80
            },
            {
                'name': 'Chi nhánh Hà Nội',
                'description': 'Chi nhánh tại Hà Nội',
                'lat': 21.0185,
                'lng': 105.8342,
                'radius_m': 120
            },
            {
                'name': 'Văn phòng đại diện',
                'description': 'Văn phòng đại diện tại trung tâm thành phố',
                'lat': 21.0085,
                'lng': 105.8142,
                'radius_m': 90
            }
        ]

        areas = []
        for area_data in areas_data:
            area, created = Area.objects.get_or_create(
                name=area_data['name'],
                defaults={
                    'description': area_data['description'],
                    'lat': area_data['lat'],
                    'lng': area_data['lng'],
                    'radius_m': area_data['radius_m'],
                    'created_by': admin,
                    'is_active': True
                }
            )
            areas.append(area)
            if created:
                self.stdout.write(f'  ✅ Tạo khu vực: {area.name}')

        self.areas = areas
        return areas

    def create_checkins(self):
        """Tạo check-in mẫu"""
        self.stdout.write('📝 Tạo check-in mẫu...')

        # Tạo check-ins trong 30 ngày qua
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        checkin_count = 0
        for user in self.users:
            # Mỗi user có 15-25 check-ins trong 30 ngày
            num_checkins = random.randint(15, 25)
            
            for i in range(num_checkins):
                # Random thời gian trong 30 ngày qua
                random_days = random.randint(0, 29)
                random_hours = random.randint(8, 17)  # Giờ làm việc
                random_minutes = random.randint(0, 59)
                
                checkin_time = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # Random khu vực
                area = random.choice(self.areas)
                
                # Random tọa độ trong khu vực
                lat_offset = random.uniform(-0.001, 0.001)
                lng_offset = random.uniform(-0.001, 0.001)
                
                lat = area.lat + lat_offset
                lng = area.lng + lng_offset
                
                # Random ghi chú
                notes = [
                    'Check-in bình thường',
                    'Đến sớm để chuẩn bị công việc',
                    'Họp team buổi sáng',
                    'Kiểm tra hệ thống',
                    'Làm việc từ xa',
                    'Họp với khách hàng',
                    'Kiểm tra tiến độ dự án',
                    'Đào tạo nhân viên mới',
                    'Báo cáo tuần',
                    'Kiểm tra kho hàng'
                ]
                
                note = random.choice(notes)
                
                checkin = Checkin.objects.create(
                    user=user,
                    area=area,
                    lat=lat,
                    lng=lng,
                    distance_m=random.uniform(0, 50),
                    note=note,
                    ip='192.168.1.100',
                    created_at=checkin_time
                )
                
                checkin_count += 1

        self.stdout.write(f'  ✅ Tạo {checkin_count} check-ins mẫu')

        return checkin_count