#!/bin/bash
# Test Environment Deployment Script
# Deploy to staging/test server with full sample data

set -e

echo "🧪 Starting NOV-RECO Test Environment Deployment..."

# Configuration
PROJECT_NAME="nov-reco-test"
PROJECT_DIR="/var/www/nov-reco-test"
USER="www-data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_status "Setting up test project directory..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/data
chown -R $USER:$USER $PROJECT_DIR

print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

print_status "Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

print_status "Setting up test environment variables..."
export DJANGO_ENVIRONMENT=test
export DJANGO_SECRET_KEY=test-secret-key-$(date +%s)
export DATABASE_NAME=data/db_test.sqlite3
export ALLOWED_HOSTS=checkin.taylaibui.vn,localhost
export SERVER_PORT=8000

print_status "Running Django setup..."
python manage.py migrate

print_status "Creating comprehensive test data..."
python manage.py shell -c "
# Import required modules
from django.contrib.auth import get_user_model
from users.models import Department
from checkin.models import Area, Checkin
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()

print('🏢 Creating departments...')
departments = []
dept_data = [
    ('IT', 'Công nghệ thông tin'),
    ('Sales', 'Kinh doanh'),
    ('Marketing', 'Tiếp thị'),
    ('HR', 'Nhân sự'),
    ('Finance', 'Tài chính'),
    ('Operations', 'Vận hành'),
    ('Customer Service', 'Chăm sóc khách hàng'),
    ('R&D', 'Nghiên cứu và phát triển'),
]

for name, description in dept_data:
    dept, created = Department.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    departments.append(dept)

print('👑 Creating admin user...')
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@nov-reco.com',
        'first_name': 'Admin',
        'last_name': 'System',
        'role': 'admin',
        'department': departments[0],
        'employee_id': 'ADM001',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()

print('👨‍💼 Creating managers...')
manager_data = [
    ('manager1', 'Nguyễn', 'Văn A', 'manager1@nov-reco.com', 'MGR001', 1),
    ('manager2', 'Trần', 'Thị B', 'manager2@nov-reco.com', 'MGR002', 2),
    ('manager3', 'Lê', 'Văn C', 'manager3@nov-reco.com', 'MGR003', 3),
    ('manager4', 'Phạm', 'Thị D', 'manager4@nov-reco.com', 'MGR004', 4),
]

for username, first, last, email, emp_id, dept_idx in manager_data:
    manager, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first,
            'last_name': last,
            'role': 'manager',
            'department': departments[dept_idx],
            'employee_id': emp_id
        }
    )
    if created:
        manager.set_password('manager123')
        manager.save()

print('👨‍💻 Creating employees...')
employee_data = [
    ('emp001', 'Hoàng', 'Văn E', 'emp001@nov-reco.com', 'EMP001'),
    ('emp002', 'Vũ', 'Thị F', 'emp002@nov-reco.com', 'EMP002'),
    ('emp003', 'Đặng', 'Văn G', 'emp003@nov-reco.com', 'EMP003'),
    ('emp004', 'Bùi', 'Thị H', 'emp004@nov-reco.com', 'EMP004'),
    ('emp005', 'Lý', 'Văn I', 'emp005@nov-reco.com', 'EMP005'),
    ('emp006', 'Võ', 'Thị K', 'emp006@nov-reco.com', 'EMP006'),
    ('emp007', 'Đinh', 'Văn L', 'emp007@nov-reco.com', 'EMP007'),
    ('emp008', 'Ngô', 'Thị M', 'emp008@nov-reco.com', 'EMP008'),
    ('emp009', 'Dương', 'Văn N', 'emp009@nov-reco.com', 'EMP009'),
    ('emp010', 'Mai', 'Thị O', 'emp010@nov-reco.com', 'EMP010'),
]

for i, (username, first, last, email, emp_id) in enumerate(employee_data):
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

print('📍 Creating areas...')
areas_data = [
    ('Văn phòng chính', 10.7769, 106.7009, 100, '123 Nguyễn Huệ, Quận 1, TP.HCM'),
    ('Chi nhánh Quận 7', 10.7308, 106.7194, 50, '456 Nguyễn Thị Thập, Quận 7, TP.HCM'),
    ('Chi nhánh Thủ Đức', 10.8142, 106.7767, 75, '789 Võ Văn Ngân, TP. Thủ Đức, TP.HCM'),
    ('Chi nhánh Bình Thạnh', 10.8022, 106.7144, 60, '321 Xô Viết Nghệ Tĩnh, Bình Thạnh, TP.HCM'),
    ('Chi nhánh Tân Bình', 10.8006, 106.6533, 80, '987 Cộng Hòa, Tân Bình, TP.HCM'),
    ('Kho Bình Dương', 10.9804, 106.6519, 200, '654 Đại lộ Bình Dương, Thuận An, Bình Dương'),
    ('Văn phòng Hà Nội', 21.0285, 105.8542, 100, '456 Hoàng Diệu, Ba Đình, Hà Nội'),
    ('Chi nhánh Đà Nẵng', 16.0544, 108.2022, 90, '789 Lê Duẩn, Hải Châu, Đà Nẵng'),
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

print('📊 Creating realistic check-in history...')
all_users = list(User.objects.filter(is_superuser=False))
base_date = timezone.now() - timedelta(days=60)

checkin_count = 0
for day in range(60):
    current_date = base_date + timedelta(days=day)
    
    # Skip weekends (realistic)
    if current_date.weekday() >= 5:
        continue
    
    # More check-ins on weekdays
    daily_checkins = random.randint(3, 12)
    
    for _ in range(daily_checkins):
        user = random.choice(all_users)
        area = random.choice(areas)
        
        # Business hours check-ins
        hour = random.randint(7, 18)
        minute = random.randint(0, 59)
        checkin_time = current_date.replace(hour=hour, minute=minute)
        
        distance = random.randint(5, min(area.radius, 50))
        
        notes = [
            'Check-in buổi sáng',
            'Họp khách hàng', 
            'Làm việc tại văn phòng',
            'Kiểm tra công việc',
            'Meeting với team',
            'Thăm khách hàng',
            'Báo cáo công việc',
            'Họp phòng ban',
            'Training nhân viên',
            'Kiểm tra chất lượng',
            '',  # Empty note
        ]
        
        checkin, created = Checkin.objects.get_or_create(
            user=user,
            area=area,
            created_at=checkin_time,
            defaults={
                'lat': area.latitude + random.uniform(-0.0005, 0.0005),
                'lng': area.longitude + random.uniform(-0.0005, 0.0005),
                'distance_m': distance,
                'note': random.choice(notes)
            }
        )
        if created:
            checkin_count += 1

print('')
print('🎉 Comprehensive test data created!')
print('')
print('📊 Final Summary:')
print(f'  👥 Total Users: {User.objects.count()}')
print(f'  🏢 Departments: {Department.objects.count()}')
print(f'  📍 Areas: {Area.objects.count()}')
print(f'  ✅ Total Check-ins: {Checkin.objects.count()}')
print('')
"

print_status "Setting up Gunicorn service for test..."
cat > /etc/systemd/system/nov-reco-test.service << EOF
[Unit]
Description=NOV-RECO Check-in System (Test Environment)
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=test"
Environment="DJANGO_SECRET_KEY=test-secret-key-$(date +%s)"
Environment="DATABASE_NAME=data/db_test.sqlite3"
Environment="ALLOWED_HOSTS=checkin.taylaibui.vn,localhost"
Environment="SERVER_PORT=8000"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx for test environment..."
cat > /etc/nginx/sites-available/nov-reco-test << EOF
server {
    listen 80;
    listen 443 ssl http2;
    server_name checkin.taylaibui.vn;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
        alias $PROJECT_DIR/static/favicon.ico;
    }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 7d;
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # SSL configuration (will be configured by Certbot)
    # ssl_certificate /etc/letsencrypt/live/checkin.taylaibui.vn/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/checkin.taylaibui.vn/privkey.pem;
}
EOF

ln -sf /etc/nginx/sites-available/nov-reco-test /etc/nginx/sites-enabled/
nginx -t

print_status "Starting test services..."
systemctl daemon-reload
systemctl enable nov-reco-test
systemctl start nov-reco-test
systemctl restart nginx

print_success "🎉 Test environment deployment completed!"
print_status "🌐 Test URL: https://checkin.taylaibui.vn"
print_status "🔧 Admin panel: https://checkin.taylaibui.vn/admin/"
print_status "👤 Test login credentials:"
print_success "  👨‍💼 Admin: admin / admin123"
print_success "  👨‍💼 Manager: manager1 / manager123"
print_success "  👨‍💻 Employee: emp001 / employee123"

print_warning "📊 Test database contains:"
print_warning "  - 8 departments with realistic names"
print_warning "  - 15+ users (admin, managers, employees)"
print_warning "  - 8 areas across Vietnam"
print_warning "  - 200+ realistic check-in records"

print_status "🔍 Service status:"
systemctl status nov-reco-test --no-pager -l

echo ""
echo "✅ Test environment is ready for comprehensive testing!"
