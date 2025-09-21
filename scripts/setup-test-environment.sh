#!/bin/bash
# Setup test environment with admin user and sample data

set -e

PROJECT_DIR="/var/www/checkin.taylaibui.vn"
ENVIRONMENT="test"

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_status "🗄️ Setting up test environment database and data..."

cd "$PROJECT_DIR"

# 1. Copy environment file
print_status "Setting up test environment configuration..."
cp config/test.env .env

# 2. Run migrations
print_status "Running database migrations..."
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py migrate

# 3. Create superuser for test
print_status "Creating admin user for test environment..."
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py shell << 'PYTHON_SCRIPT'
from django.contrib.auth import get_user_model
from users.models import UserRole

User = get_user_model()

# Create superuser if not exists
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@checkin.reco.vn',
        password='admin123',
        first_name='Admin',
        last_name='Test',
        role=UserRole.ADMIN,
        employee_id='ADMIN001',
        department='IT'
    )
    print("✅ Created admin user: admin / admin123")
else:
    print("✅ Admin user already exists")

# Create sample manager
if not User.objects.filter(username='manager').exists():
    manager = User.objects.create_user(
        username='manager',
        email='manager@checkin.reco.vn',
        password='manager123',
        first_name='Manager',
        last_name='Test',
        role=UserRole.MANAGER,
        employee_id='MGR001',
        department='Quản lý'
    )
    print("✅ Created manager user: manager / manager123")
else:
    print("✅ Manager user already exists")

# Create sample employee
if not User.objects.filter(username='employee').exists():
    employee = User.objects.create_user(
        username='employee',
        email='employee@checkin.reco.vn',
        password='employee123',
        first_name='Employee',
        last_name='Test',
        role=UserRole.EMPLOYEE,
        employee_id='EMP001',
        department='Kỹ thuật'
    )
    print("✅ Created employee user: employee / employee123")
else:
    print("✅ Employee user already exists")

print("✅ User setup completed!")
PYTHON_SCRIPT

# 4. Create sample areas
print_status "Creating sample areas..."
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py shell << 'PYTHON_SCRIPT'
from checkin.models import Area

# Create sample areas if not exist
areas_data = [
    {
        'name': 'Khu vực tự do',
        'description': 'Khu vực check-in tự do cho nhân viên',
        'lat': 20.997042,
        'lng': 105.803160,
        'radius': 100
    },
    {
        'name': 'Văn phòng chính',
        'description': 'Văn phòng chính NOV-RECO',
        'lat': 21.028511,
        'lng': 105.804817,
        'radius': 50
    },
    {
        'name': 'Chi nhánh Hà Nội',
        'description': 'Chi nhánh Hà Nội',
        'lat': 21.0285,
        'lng': 105.8542,
        'radius': 75
    }
]

for area_data in areas_data:
    area, created = Area.objects.get_or_create(
        name=area_data['name'],
        defaults=area_data
    )
    if created:
        print(f"✅ Created area: {area.name}")
    else:
        print(f"✅ Area already exists: {area.name}")

print("✅ Areas setup completed!")
PYTHON_SCRIPT

# 5. Collect static files
print_status "Collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py collectstatic --noinput

# 6. Fix permissions
print_status "Fixing permissions..."
sudo mkdir -p logs
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 7. Restart service
print_status "Restarting Django service..."
sudo systemctl restart checkin-taylaibui-test

# 8. Test
print_status "Testing website..."
sleep 3

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://103.15.51.66 || echo "000")
if [ "$HTTP_CODE" == "200" ]; then
    print_success "✅ Website is working: http://103.15.51.66"
else
    print_error "❌ Website error (HTTP $HTTP_CODE)"
fi

CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://103.15.51.66/static/css/home.css || echo "000")
if [ "$CSS_CODE" == "200" ]; then
    print_success "✅ Static files working"
else
    print_error "❌ Static files error (HTTP $CSS_CODE)"
fi

print_success "🎉 Test environment setup completed!"
echo
echo "📋 Test Users Created:"
echo "   👑 Admin: admin / admin123"
echo "   👨‍💼 Manager: manager / manager123"  
echo "   👤 Employee: employee / employee123"
echo
echo "🌐 Access URLs:"
echo "   Website: http://103.15.51.66"
echo "   Domain: http://checkin.taylaibui.vn"
echo "   Admin: http://103.15.51.66/admin/"
echo
