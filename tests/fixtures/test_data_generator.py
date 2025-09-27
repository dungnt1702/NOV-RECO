"""
Test data generator for all modules
Automatically creates comprehensive test data
"""

import os
import sys

import django
from django.core.management import call_command
from django.db import transaction

# Add project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import random
from datetime import datetime, timedelta

from apps.area.models import Area
from apps.checkin.models import Checkin
from apps.users.models import Department, User, UserRole


class TestDataGenerator:
    """Generate comprehensive test data for all modules"""

    def __init__(self):
        self.departments = []
        self.users = []
        self.areas = []
        self.checkins = []

    def generate_all_data(self):
        """Generate all test data"""
        print("🔄 Generating comprehensive test data...")

        with transaction.atomic():
            self.generate_departments()
            self.generate_users()
            self.generate_areas()
            self.generate_checkins()

        print("✅ Test data generation completed!")
        self.print_summary()

    def generate_departments(self):
        """Generate test departments"""
        department_data = [
            {"name": "Phòng Hành chính", "description": "Quản lý hành chính tổng hợp"},
            {"name": "Phòng IT", "description": "Công nghệ thông tin và hệ thống"},
            {
                "name": "Phòng Kinh doanh",
                "description": "Kinh doanh và phát triển thị trường",
            },
            {"name": "Phòng Nhân sự", "description": "Quản lý nhân sự và đào tạo"},
            {"name": "Phòng Kế toán", "description": "Kế toán và tài chính"},
        ]

        for data in department_data:
            dept, created = Department.objects.get_or_create(
                name=data["name"], defaults={"description": data["description"]}
            )
            self.departments.append(dept)

    def generate_users(self):
        """Generate test users with different roles"""
        # Admin users
        admin_data = [
            {
                "username": "admin",
                "email": "admin@nov-reco.com",
                "first_name": "Admin",
                "last_name": "System",
                "role": UserRole.ADMIN,
            },
            {
                "username": "superadmin",
                "email": "superadmin@nov-reco.com",
                "first_name": "Super",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
            },
        ]

        # Manager users
        manager_data = [
            {
                "username": "manager_it",
                "email": "manager.it@nov-reco.com",
                "first_name": "Nguyễn",
                "last_name": "Văn IT",
                "role": UserRole.MANAGER,
            },
            {
                "username": "manager_hr",
                "email": "manager.hr@nov-reco.com",
                "first_name": "Trần",
                "last_name": "Thị HR",
                "role": UserRole.MANAGER,
            },
            {
                "username": "manager_sales",
                "email": "manager.sales@nov-reco.com",
                "first_name": "Lê",
                "last_name": "Văn Sales",
                "role": UserRole.MANAGER,
            },
        ]

        # Employee users
        employee_data = [
            {
                "username": "emp001",
                "email": "emp001@nov-reco.com",
                "first_name": "Nguyễn",
                "last_name": "Văn A",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp002",
                "email": "emp002@nov-reco.com",
                "first_name": "Trần",
                "last_name": "Thị B",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp003",
                "email": "emp003@nov-reco.com",
                "first_name": "Lê",
                "last_name": "Văn C",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp004",
                "email": "emp004@nov-reco.com",
                "first_name": "Phạm",
                "last_name": "Thị D",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp005",
                "email": "emp005@nov-reco.com",
                "first_name": "Hoàng",
                "last_name": "Văn E",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp006",
                "email": "emp006@nov-reco.com",
                "first_name": "Vũ",
                "last_name": "Thị F",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp007",
                "email": "emp007@nov-reco.com",
                "first_name": "Đặng",
                "last_name": "Văn G",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp008",
                "email": "emp008@nov-reco.com",
                "first_name": "Bùi",
                "last_name": "Thị H",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp009",
                "email": "emp009@nov-reco.com",
                "first_name": "Đỗ",
                "last_name": "Văn I",
                "role": UserRole.EMPLOYEE,
            },
            {
                "username": "emp010",
                "email": "emp010@nov-reco.com",
                "first_name": "Hồ",
                "last_name": "Thị J",
                "role": UserRole.EMPLOYEE,
            },
        ]

        all_users = admin_data + manager_data + employee_data

        for user_data in all_users:
            # Assign random department
            department = random.choice(self.departments)

            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "role": user_data["role"],
                    "department": department,
                    "is_staff": user_data["role"] in [UserRole.ADMIN, UserRole.MANAGER],
                    "is_superuser": user_data["role"] == UserRole.ADMIN,
                },
            )

            if created:
                user.set_password("testpass123")
                user.save()

            self.users.append(user)

    def generate_areas(self):
        """Generate test areas"""
        area_data = [
            {
                "name": "Văn phòng chính",
                "description": "Tòa nhà văn phòng chính của công ty",
                "lat": 10.762622,
                "lng": 106.660172,
                "radius_m": 50,
            },
            {
                "name": "Chi nhánh Quận 1",
                "description": "Chi nhánh tại Quận 1, TP.HCM",
                "lat": 10.7769,
                "lng": 106.7009,
                "radius_m": 100,
            },
            {
                "name": "Chi nhánh Quận 7",
                "description": "Chi nhánh tại Quận 7, TP.HCM",
                "lat": 10.7329,
                "lng": 106.7229,
                "radius_m": 80,
            },
            {
                "name": "Kho hàng Bình Dương",
                "description": "Kho hàng tại Bình Dương",
                "lat": 10.9804,
                "lng": 106.6519,
                "radius_m": 200,
            },
            {
                "name": "Showroom Đồng Nai",
                "description": "Showroom tại Đồng Nai",
                "lat": 10.9447,
                "lng": 106.8243,
                "radius_m": 150,
            },
            {
                "name": "Văn phòng đại diện Hà Nội",
                "description": "Văn phòng đại diện tại Hà Nội",
                "lat": 21.0285,
                "lng": 105.8542,
                "radius_m": 120,
            },
            {
                "name": "Trung tâm đào tạo",
                "description": "Trung tâm đào tạo nhân viên",
                "lat": 10.7626,
                "lng": 106.6601,
                "radius_m": 60,
            },
        ]

        admin_user = User.objects.filter(role=UserRole.ADMIN).first()

        for data in area_data:
            area, created = Area.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "lat": data["lat"],
                    "lng": data["lng"],
                    "radius_m": data["radius_m"],
                    "is_active": True,
                    "created_by": admin_user,
                },
            )
            self.areas.append(area)

    def generate_checkins(self):
        """Generate test check-ins"""
        # Get random users and areas
        users = User.objects.filter(role=UserRole.EMPLOYEE)
        areas = Area.objects.filter(is_active=True)

        if not users.exists() or not areas.exists():
            return

        # Generate check-ins for the last 30 days
        start_date = datetime.now() - timedelta(days=30)

        for i in range(300):  # Generate 300 check-ins
            user = random.choice(users)
            area = random.choice(areas)

            # Random date within last 30 days
            random_days = random.randint(0, 30)
            random_hours = random.randint(8, 18)  # Working hours
            random_minutes = random.randint(0, 59)

            checkin_time = start_date + timedelta(
                days=random_days, hours=random_hours, minutes=random_minutes
            )

            # Random location near the area (within radius)
            lat_offset = random.uniform(-0.001, 0.001)  # ~100m offset
            lng_offset = random.uniform(-0.001, 0.001)

            checkin = Checkin.objects.create(
                user=user,
                area=area,
                lat=area.lat + lat_offset,
                lng=area.lng + lng_offset,
                photo=f"test_photos/checkin_{i+1}.jpg",
                note=f"Test check-in #{i+1}",
                created_at=checkin_time,
                distance_m=random.randint(0, area.radius_m),
                ip="127.0.0.1",
                user_agent="Test User Agent",
            )

            self.checkins.append(checkin)

    def print_summary(self):
        """Print summary of generated data"""
        print("\n📊 Test Data Summary:")
        print(f"   Departments: {Department.objects.count()}")
        print(f"   Users: {User.objects.count()}")
        print(f"   - Admin: {User.objects.filter(role=UserRole.ADMIN).count()}")
        print(f"   - Manager: {User.objects.filter(role=UserRole.MANAGER).count()}")
        print(f"   - Employee: {User.objects.filter(role=UserRole.EMPLOYEE).count()}")
        print(f"   Areas: {Area.objects.count()}")
        print(f"   Check-ins: {Checkin.objects.count()}")


if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_all_data()
