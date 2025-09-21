#!/bin/bash
# Test Environment Deployment Script for checkin.taylaibui.vn
# This script deploys NOV-RECO in TEST mode on the server

set -e

echo "🧪 Deploying NOV-RECO in TEST environment..."

# Configuration
PROJECT_DIR="/var/www/checkin.taylaibui.vn"
USER="www-data"
DOMAIN="checkin.taylaibui.vn"
ENVIRONMENT="test"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

print_status "Setting up project directory..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/data

print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx git

print_status "Setting up Git repository..."
cd $PROJECT_DIR
git config --global --add safe.directory $PROJECT_DIR
chown -R $USER:$USER $PROJECT_DIR

print_status "Setting up Python environment..."
sudo -u $USER python3 -m venv venv
sudo -u $USER ./venv/bin/pip install --upgrade pip

print_status "Installing Python dependencies..."
sudo -u $USER ./venv/bin/pip install -r requirements.txt

print_status "Setting up TEST environment..."
sudo -u $USER cp config/test.env .env

print_status "Running Django setup for TEST environment..."
sudo -u $USER DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py migrate
sudo -u $USER DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py collectstatic --noinput

print_status "Creating test admin user..."
sudo -u $USER DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin123')
    print('✅ Test admin user created: admin/admin123')
else:
    print('ℹ️ Admin user already exists')
"

print_status "Creating sample data for testing..."
sudo -u $USER DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py shell -c "
# Create sample users and areas for testing
from django.contrib.auth import get_user_model
from users.models import UserRole
from checkin.models import Area
from django.contrib.auth.models import Group

User = get_user_model()

# Create test users
test_users = [
    {'username': 'manager_test', 'email': 'manager@test.com', 'password': 'test123', 'role': 'MANAGER'},
    {'username': 'employee_test', 'email': 'employee@test.com', 'password': 'test123', 'role': 'EMPLOYEE'},
]

for user_data in test_users:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        print(f'✅ Test user created: {user_data[\"username\"]}/test123')

print('✅ Sample data created for testing')
"

print_status "Setting up systemd service for TEST..."
tee /etc/systemd/system/checkin-taylaibui-test.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System - TEST Environment
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=test"
Environment="DJANGO_SECRET_KEY=nov-reco-test-secret-key-for-checkin-taylaibui-vn"
Environment="ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1"
Environment="DJANGO_DEBUG=1"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 project.wsgi:application --timeout 120 --log-level debug
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx for TEST environment..."
tee /etc/nginx/sites-available/$DOMAIN-test > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN 103.15.51.66;

    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1d;
    }

    # Favicon
    location = /favicon.ico {
        alias $PROJECT_DIR/staticfiles/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Longer timeout for debugging
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable test site
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/$DOMAIN
ln -sf /etc/nginx/sites-available/$DOMAIN-test /etc/nginx/sites-enabled/

nginx -t

print_status "Starting TEST services..."
systemctl daemon-reload
systemctl enable checkin-taylaibui-test
systemctl start checkin-taylaibui-test
systemctl restart nginx

# Wait for services to start
sleep 10

print_status "Testing TEST environment..."
if curl -s http://localhost:8000 > /dev/null; then
    print_success "✅ Django server responding"
else
    print_warning "❌ Django server not responding"
fi

if curl -s http://$DOMAIN > /dev/null; then
    print_success "✅ Website accessible via domain"
else
    print_warning "❌ Website not accessible via domain"
fi

print_success "🎉 TEST Environment Deployment completed!"
print_status "🌐 Website: http://$DOMAIN"
print_status "🔧 Admin panel: http://$DOMAIN/admin/"
print_status "👤 Test login: admin / admin123"
print_status "👤 Manager test: manager_test / test123"
print_status "👤 Employee test: employee_test / test123"

print_warning "📝 This is TEST environment for checkin.taylaibui.vn:"
print_warning "  - Server IP: 103.15.51.66"
print_warning "  - Environment: TEST (DEBUG=True)"
print_warning "  - Database: SQLite (test data)"
print_warning "  - Security: Relaxed for testing"

print_warning "📝 This is TEST environment with:"
print_warning "- DEBUG=True (detailed error messages)"
print_warning "- SQLite database"
print_warning "- Console email backend"
print_warning "- Relaxed security settings"

echo ""
print_status "🔧 Service management commands:"
echo "  - Check status: sudo systemctl status checkin-taylaibui-test"
echo "  - View logs: sudo journalctl -u checkin-taylaibui-test -f"
echo "  - Restart: sudo systemctl restart checkin-taylaibui-test"
