#!/usr/bin/env python3
"""
Script to create comprehensive test data for NOV-RECO Check-in System
Usage: python scripts/create-test-data.py [local|test|production]
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserRole, Department
from checkin.models import Area, Checkin
from django.core.files.base import ContentFile
import json

User = get_user_model()

def print_status(message):
    print(f"\033[0;34m[INFO]\033[0m {message}")

def print_success(message):
    print(f"\033[0;32m[SUCCESS]\033[0m {message}")

def print_error(message):
    print(f"\033[0;31m[ERROR]\033[0m {message}")

def create_departments():
    """Create test departments"""
    departments_data = [
        {'name': 'Công nghệ thông tin', 'description': 'Phòng ban phát triển và quản lý hệ thống IT'},
        {'name': 'Nhân sự', 'description': 'Phòng ban quản lý nhân lực và tuyển dụng'},
        {'name': 'Kế toán', 'description': 'Phòng ban quản lý tài chính và kế toán'},
        {'name': 'Marketing', 'description': 'Phòng ban tiếp thị và quảng cáo'},
        {'name': 'Kinh doanh', 'description': 'Phòng ban bán hàng và phát triển kinh doanh'},
        {'name': 'Vận hành', 'description': 'Phòng ban vận hành và logistics'},
        {'name': 'Chăm sóc khách hàng', 'description': 'Phòng ban hỗ trợ và chăm sóc khách hàng'},
    ]
    
    created_departments = []
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        created_departments.append(dept)
        if created:
            print_success(f"✅ Created department: {dept.name}")
        else:
            print_status(f"📋 Department exists: {dept.name}")
    
    return created_departments

def create_areas():
    """Create test check-in areas"""
    areas_data = [
        {
            'name': 'Văn phòng chính - Tầng 1',
            'description': 'Khu vực làm việc chính tầng 1 - Phòng IT, Marketing',
            'lat': 10.7769,
            'lng': 106.7009,
            'radius_m': 50
        },
        {
            'name': 'Văn phòng chính - Tầng 2', 
            'description': 'Khu vực làm việc chính tầng 2 - Phòng Nhân sự, Kế toán',
            'lat': 10.7770,
            'lng': 106.7010,
            'radius_m': 50
        },
        {
            'name': 'Văn phòng chính - Tầng 3',
            'description': 'Khu vực làm việc chính tầng 3 - Phòng Kinh doanh, CSKH',
            'lat': 10.7771,
            'lng': 106.7011,
            'radius_m': 50
        },
        {
            'name': 'Khu vực tự do',
            'description': 'Khu vực check-in linh hoạt - Không giới hạn vị trí',
            'lat': 10.7760,
            'lng': 106.7000,
            'radius_m': 1000
        },
        {
            'name': 'Chi nhánh Quận 1',
            'description': 'Văn phòng chi nhánh tại trung tâm Quận 1',
            'lat': 10.7756,
            'lng': 106.7019,
            'radius_m': 30
        },
        {
            'name': 'Chi nhánh Quận 7',
            'description': 'Văn phòng chi nhánh tại khu vực Phú Mỹ Hưng',
            'lat': 10.7411,
            'lng': 106.7117,
            'radius_m': 40
        },
        {
            'name': 'Kho hàng Bình Dương',
            'description': 'Khu vực kho hàng và logistics tại Bình Dương',
            'lat': 10.9804,
            'lng': 106.6519,
            'radius_m': 100
        },
        {
            'name': 'Showroom Nguyễn Huệ',
            'description': 'Showroom trưng bày sản phẩm phố đi bộ Nguyễn Huệ',
            'lat': 10.7743,
            'lng': 106.7021,
            'radius_m': 25
        }
    ]
    
    created_areas = []
    for area_data in areas_data:
        area, created = Area.objects.get_or_create(
            name=area_data['name'],
            defaults={
                'description': area_data['description'],
                'lat': Decimal(str(area_data['lat'])),
                'lng': Decimal(str(area_data['lng'])),
                'radius_m': area_data['radius_m'],
                'is_active': True
            }
        )
        created_areas.append(area)
        if created:
            print_success(f"✅ Created area: {area.name}")
        else:
            print_status(f"🗺️  Area exists: {area.name}")
    
    return created_areas

def create_users(departments):
    """Create test users with different roles"""
    users_data = [
        # Admin users
        {
            'username': 'admin',
            'email': 'admin@nov-reco.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'System',
            'role': UserRole.ADMIN,
            'employee_id': 'ADMIN001',
            'department': 'Công nghệ thông tin',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'username': 'admin.it',
            'email': 'admin.it@nov-reco.com',
            'password': 'admin123',
            'first_name': 'Nguyễn',
            'last_name': 'Quản Trị',
            'role': UserRole.ADMIN,
            'employee_id': 'IT001',
            'department': 'Công nghệ thông tin',
            'is_superuser': False,
            'is_staff': True
        },
        
        # Manager users
        {
            'username': 'manager.it',
            'email': 'manager.it@nov-reco.com',
            'password': 'manager123',
            'first_name': 'Trần',
            'last_name': 'Văn Minh',
            'role': UserRole.MANAGER,
            'employee_id': 'MGR001',
            'department': 'Công nghệ thông tin'
        },
        {
            'username': 'manager.hr',
            'email': 'manager.hr@nov-reco.com',
            'password': 'manager123',
            'first_name': 'Lê',
            'last_name': 'Thị Hoa',
            'role': UserRole.MANAGER,
            'employee_id': 'MGR002',
            'department': 'Nhân sự'
        },
        {
            'username': 'manager.sales',
            'email': 'manager.sales@nov-reco.com',
            'password': 'manager123',
            'first_name': 'Phạm',
            'last_name': 'Văn Đức',
            'role': UserRole.MANAGER,
            'employee_id': 'MGR003',
            'department': 'Kinh doanh'
        },
        {
            'username': 'manager.marketing',
            'email': 'manager.marketing@nov-reco.com',
            'password': 'manager123',
            'first_name': 'Vũ',
            'last_name': 'Thị Mai',
            'role': UserRole.MANAGER,
            'employee_id': 'MGR004',
            'department': 'Marketing'
        },
        
        # Employee users
        {
            'username': 'dev.frontend',
            'email': 'dev.frontend@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Nguyễn',
            'last_name': 'Văn An',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'DEV001',
            'department': 'Công nghệ thông tin'
        },
        {
            'username': 'dev.backend',
            'email': 'dev.backend@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Trần',
            'last_name': 'Thị Bình',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'DEV002',
            'department': 'Công nghệ thông tin'
        },
        {
            'username': 'hr.specialist',
            'email': 'hr.specialist@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Lê',
            'last_name': 'Văn Cường',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'HR001',
            'department': 'Nhân sự'
        },
        {
            'username': 'accountant.senior',
            'email': 'accountant.senior@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Phạm',
            'last_name': 'Thị Diệu',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'ACC001',
            'department': 'Kế toán'
        },
        {
            'username': 'sales.rep1',
            'email': 'sales.rep1@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Hoàng',
            'last_name': 'Văn Đạt',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'SALES001',
            'department': 'Kinh doanh'
        },
        {
            'username': 'sales.rep2',
            'email': 'sales.rep2@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Vũ',
            'last_name': 'Thị Ê',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'SALES002',
            'department': 'Kinh doanh'
        },
        {
            'username': 'marketing.content',
            'email': 'marketing.content@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Đặng',
            'last_name': 'Văn Phong',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'MKT001',
            'department': 'Marketing'
        },
        {
            'username': 'marketing.digital',
            'email': 'marketing.digital@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Bùi',
            'last_name': 'Thị Giang',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'MKT002',
            'department': 'Marketing'
        },
        {
            'username': 'operations.lead',
            'email': 'operations.lead@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Cao',
            'last_name': 'Văn Hải',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'OPS001',
            'department': 'Vận hành'
        },
        {
            'username': 'support.agent1',
            'email': 'support.agent1@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Đinh',
            'last_name': 'Thị Linh',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'SUP001',
            'department': 'Chăm sóc khách hàng'
        },
        {
            'username': 'support.agent2',
            'email': 'support.agent2@nov-reco.com',
            'password': 'employee123',
            'first_name': 'Đỗ',
            'last_name': 'Văn Khánh',
            'role': UserRole.EMPLOYEE,
            'employee_id': 'SUP002',
            'department': 'Chăm sóc khách hàng'
        }
    ]
    
    # Create department lookup
    dept_lookup = {dept.name: dept for dept in departments}
    
    created_users = []
    for user_data in users_data:
        # Get department
        dept = dept_lookup.get(user_data['department'])
        
        # Check if user exists
        if User.objects.filter(username=user_data['username']).exists():
            user = User.objects.get(username=user_data['username'])
            print_status(f"👤 User exists: {user.username}")
        else:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                employee_id=user_data['employee_id'],
                department=dept,
                is_superuser=user_data.get('is_superuser', False),
                is_staff=user_data.get('is_staff', False)
            )
            print_success(f"✅ Created user: {user.username} ({user.get_display_name()})")
        
        created_users.append(user)
    
    return created_users

def create_sample_checkins(users, areas, days_back=7, checkins_per_day=3):
    """Create sample check-in records"""
    print_status(f"Creating sample check-ins for last {days_back} days...")
    
    # Sample notes for check-ins
    sample_notes = [
        "Check-in thường ngày",
        "Họp team buổi sáng",
        "Làm việc dự án mới", 
        "Gặp khách hàng",
        "Hoàn thành báo cáo",
        "Tham gia training",
        "Check-in từ chi nhánh",
        "Làm việc remote",
        "Họp với đối tác",
        "Cập nhật tiến độ công việc",
        "Thực hiện demo sản phẩm",
        "Review code với team",
        "Chuẩn bị presentation",
        "Tham gia workshop",
        ""  # Empty note
    ]
    
    created_checkins = 0
    
    for day_offset in range(days_back):
        # Calculate date
        check_date = datetime.now() - timedelta(days=day_offset)
        
        # Random number of check-ins for this day (1-5)
        daily_checkins = random.randint(1, checkins_per_day + 2)
        
        # Select random users for today
        daily_users = random.sample(users, min(len(users), daily_checkins))
        
        for user in daily_users:
            # Random time during work hours (8:00 - 18:00)
            hour = random.randint(8, 17)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            checkin_time = check_date.replace(
                hour=hour, 
                minute=minute, 
                second=second,
                microsecond=0
            )
            
            # Select random area
            area = random.choice(areas)
            
            # Add small random offset to coordinates (within radius)
            lat_offset = random.uniform(-0.0005, 0.0005)  # ~50m
            lng_offset = random.uniform(-0.0005, 0.0005)  # ~50m
            
            actual_lat = float(area.lat) + lat_offset
            actual_lng = float(area.lng) + lng_offset
            
            # Calculate distance (simplified)
            distance = random.randint(5, min(area.radius_m, 45))
            
            # Random note
            note = random.choice(sample_notes)
            
            # Check if checkin already exists for this user on this date
            existing = Checkin.objects.filter(
                user=user,
                created_at__date=checkin_time.date()
            ).first()
            
            if not existing:
                # Create checkin
                checkin = Checkin.objects.create(
                    user=user,
                    area=area,
                    lat=Decimal(str(actual_lat)),
                    lng=Decimal(str(actual_lng)),
                    distance_m=distance,
                    note=note,
                    created_at=checkin_time
                )
                created_checkins += 1
                
                if created_checkins <= 5:  # Show first few
                    print_success(f"✅ Created check-in: {user.get_display_name()} at {area.name} ({checkin_time.strftime('%d/%m %H:%M')})")
    
    print_success(f"📊 Created {created_checkins} sample check-ins")
    return created_checkins

def create_summary_data():
    """Create and display summary of test data"""
    print_status("\n📊 TEST DATA SUMMARY:")
    print_status("=" * 50)
    
    # Count data
    users_count = User.objects.count()
    departments_count = Department.objects.count()
    areas_count = Area.objects.count()
    checkins_count = Checkin.objects.count()
    
    print_success(f"👥 Users: {users_count}")
    print_success(f"🏢 Departments: {departments_count}")
    print_success(f"🗺️  Areas: {areas_count}")
    print_success(f"📍 Check-ins: {checkins_count}")
    
    # Show user breakdown by role
    admin_count = User.objects.filter(role=UserRole.ADMIN).count()
    manager_count = User.objects.filter(role=UserRole.MANAGER).count()
    employee_count = User.objects.filter(role=UserRole.EMPLOYEE).count()
    
    print_status(f"\n👤 USER ROLES:")
    print_success(f"  🔑 Admins: {admin_count}")
    print_success(f"  👔 Managers: {manager_count}")
    print_success(f"  💼 Employees: {employee_count}")
    
    # Show recent check-ins
    recent_checkins = Checkin.objects.select_related('user', 'area').order_by('-created_at')[:5]
    if recent_checkins:
        print_status(f"\n📍 RECENT CHECK-INS:")
        for checkin in recent_checkins:
            print_success(f"  {checkin.user.get_display_name()} → {checkin.area.name} ({checkin.created_at.strftime('%d/%m %H:%M')})")

def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    print_status(f"🚀 Creating test data for {environment.upper()} environment...")
    print_status("=" * 60)
    
    try:
        # 1. Create departments
        print_status("1️⃣  Creating departments...")
        departments = create_departments()
        
        # 2. Create areas
        print_status("\n2️⃣  Creating check-in areas...")
        areas = create_areas()
        
        # 3. Create users
        print_status("\n3️⃣  Creating users...")
        users = create_users(departments)
        
        # 4. Create sample check-ins
        print_status("\n4️⃣  Creating sample check-ins...")
        if environment == 'local':
            create_sample_checkins(users, areas, days_back=14, checkins_per_day=4)
        elif environment == 'test':
            create_sample_checkins(users, areas, days_back=10, checkins_per_day=3)
        else:  # production
            create_sample_checkins(users, areas, days_back=3, checkins_per_day=2)
        
        # 5. Show summary
        create_summary_data()
        
        print_status("\n" + "=" * 60)
        print_success("🎉 TEST DATA CREATION COMPLETED!")
        print_status("\n🔑 LOGIN CREDENTIALS:")
        print_status("  👑 Admin: admin / admin123")
        print_status("  👔 Manager: manager.it / manager123")
        print_status("  💼 Employee: dev.frontend / employee123")
        print_status("\n🌐 Access URLs:")
        if environment == 'local':
            print_status("  Local: http://127.0.0.1:3000")
        elif environment == 'test':
            print_status("  Test: http://checkin.taylaibui.vn")
        else:
            print_status("  Production: http://reco.qly.vn")
        
    except Exception as e:
        print_error(f"❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
