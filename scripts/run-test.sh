#!/bin/bash
# Test Environment Runner with Full Sample Data

# Set test environment variables
export DJANGO_ENVIRONMENT=test
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY=test-secret-key-change-me
export DATABASE_ENGINE=django.db.backends.sqlite3
export DATABASE_NAME=data/db_test.sqlite3
export ALLOWED_HOSTS=checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0
export SERVER_PORT=8000

echo "🧪 Starting NOV-RECO Check-in System (Test Environment)"
echo "📍 Environment: $DJANGO_ENVIRONMENT"
echo "🐛 Debug mode: $DJANGO_DEBUG"
echo "🗄️ Database: $DATABASE_NAME"
echo "🌐 Server will run on: http://localhost:$SERVER_PORT"
echo "🌐 Production test URL: https://checkin.taylaibui.vn"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create test database with full sample data
echo "🗄️ Setting up test database..."
python manage.py migrate

# Check if test database is empty and create sample data
echo "📊 Creating comprehensive sample data..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
from users.models import Department
from checkin.models import Area, Checkin
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

print('🏢 Creating departments...')
departments = []
dept_names = ['IT', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Customer Service']
for dept_name in dept_names:
    dept, created = Department.objects.get_or_create(name=dept_name)
    departments.append(dept)
    if created:
        print(f'  ✅ Created department: {dept_name}')

print('👥 Creating users...')
# Create admin
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@nov-reco.com',
        'first_name': 'Admin',
        'last_name': 'System',
        'role': 'admin',
        'department': departments[0],  # IT
        'employee_id': 'ADM001',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print('  ✅ Created admin user: admin/admin123')

# Create managers
manager_names = [
    ('manager1', 'Nguyễn', 'Văn A', 'manager1@nov-reco.com', 'MGR001'),
    ('manager2', 'Trần', 'Thị B', 'manager2@nov-reco.com', 'MGR002'),
    ('manager3', 'Lê', 'Văn C', 'manager3@nov-reco.com', 'MGR003'),
]

managers = []
for i, (username, first, last, email, emp_id) in enumerate(manager_names):
    manager, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first,
            'last_name': last,
            'role': 'manager',
            'department': departments[i + 1],  # Sales, Marketing, HR
            'employee_id': emp_id
        }
    )
    if created:
        manager.set_password('manager123')
        manager.save()
        managers.append(manager)
        print(f'  ✅ Created manager: {username}/manager123')

# Create employees
employee_names = [
    ('emp001', 'Phạm', 'Thị D', 'emp001@nov-reco.com', 'EMP001'),
    ('emp002', 'Hoàng', 'Văn E', 'emp002@nov-reco.com', 'EMP002'),
    ('emp003', 'Vũ', 'Thị F', 'emp003@nov-reco.com', 'EMP003'),
    ('emp004', 'Đặng', 'Văn G', 'emp004@nov-reco.com', 'EMP004'),
    ('emp005', 'Bùi', 'Thị H', 'emp005@nov-reco.com', 'EMP005'),
    ('emp006', 'Lý', 'Văn I', 'emp006@nov-reco.com', 'EMP006'),
    ('emp007', 'Võ', 'Thị K', 'emp007@nov-reco.com', 'EMP007'),
    ('emp008', 'Đinh', 'Văn L', 'emp008@nov-reco.com', 'EMP008'),
]

employees = []
for i, (username, first, last, email, emp_id) in enumerate(employee_names):
    employee, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first,
            'last_name': last,
            'role': 'employee',
            'department': departments[i % len(departments)],
            'employee_id': emp_id
        }
    )
    if created:
        employee.set_password('employee123')
        employee.save()
        employees.append(employee)
        print(f'  ✅ Created employee: {username}/employee123')

print('📍 Creating areas...')
areas_data = [
    ('Văn phòng chính', 10.7769, 106.7009, 100, '123 Nguyễn Huệ, Quận 1, TP.HCM'),
    ('Chi nhánh Quận 7', 10.7308, 106.7194, 50, '456 Nguyễn Thị Thập, Quận 7, TP.HCM'),
    ('Chi nhánh Thủ Đức', 10.8142, 106.7767, 75, '789 Võ Văn Ngân, TP. Thủ Đức, TP.HCM'),
    ('Chi nhánh Bình Thạnh', 10.8022, 106.7144, 60, '321 Xô Viết Nghệ Tĩnh, Bình Thạnh, TP.HCM'),
    ('Kho Bình Dương', 10.9804, 106.6519, 200, '654 Đại lộ Bình Dương, Thuận An, Bình Dương'),
]

areas = []
for name, lat, lng, radius, address in areas_data:
    area, created = Area.objects.get_or_create(
        name=name,
        defaults={
            'latitude': lat,
            'longitude': lng,
            'radius': radius,
            'address': address,
            'created_by': admin
        }
    )
    areas.append(area)
    if created:
        print(f'  ✅ Created area: {name}')

print('📊 Creating sample check-ins...')
# Create check-ins for the last 30 days
all_users = list(User.objects.filter(is_superuser=False))
base_date = timezone.now() - timedelta(days=30)

checkin_count = 0
for day in range(30):
    current_date = base_date + timedelta(days=day)
    
    # Random number of check-ins per day (0-8)
    daily_checkins = random.randint(0, 8)
    
    for _ in range(daily_checkins):
        user = random.choice(all_users)
        area = random.choice(areas)
        
        # Random time during business hours
        hour = random.randint(7, 18)
        minute = random.randint(0, 59)
        checkin_time = current_date.replace(hour=hour, minute=minute)
        
        # Random distance within area radius
        distance = random.randint(5, area.radius)
        
        # Random notes (sometimes empty)
        notes = [
            'Check-in buổi sáng',
            'Họp khách hàng', 
            'Làm việc tại văn phòng',
            'Kiểm tra công việc',
            'Meeting với team',
            '',  # Empty note
            'Thăm khách hàng',
            'Báo cáo công việc'
        ]
        
        checkin, created = Checkin.objects.get_or_create(
            user=user,
            area=area,
            created_at=checkin_time,
            defaults={
                'lat': area.latitude + random.uniform(-0.001, 0.001),
                'lng': area.longitude + random.uniform(-0.001, 0.001),
                'distance_m': distance,
                'note': random.choice(notes)
            }
        )
        if created:
            checkin_count += 1

print(f'  ✅ Created {checkin_count} sample check-ins')

print('')
print('🎉 Test environment sample data created successfully!')
print('')
print('📊 Summary:')
print(f'  👥 Users: {User.objects.count()}')
print(f'  🏢 Departments: {Department.objects.count()}')
print(f'  📍 Areas: {Area.objects.count()}')
print(f'  ✅ Check-ins: {Checkin.objects.count()}')
print('')
print('🔑 Login credentials:')
print('  👨‍💼 Admin: admin / admin123')
print('  👨‍💼 Managers: manager1, manager2, manager3 / manager123')
print('  👨‍💻 Employees: emp001-emp008 / employee123')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "🎉 Test environment setup completed!"
echo "📊 Database contains comprehensive sample data"
echo "🔑 Login with: admin/admin123, manager1/manager123, emp001/employee123"
echo ""

# Start test server
echo "🚀 Starting test server..."
python manage.py runserver $SERVER_PORT
