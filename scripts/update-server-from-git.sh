#!/bin/bash
# Update Server from Git Script
# Usage: ./scripts/update-server-from-git.sh [test|production]

ENVIRONMENT=${1:-"test"}
PROJECT_DIR="/var/www/checkin.taylaibui.vn"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔄 Updating server from Git repository..."

# Validate environment
case $ENVIRONMENT in
    test|production)
        ;;
    *)
        print_error "Invalid environment. Use: test or production"
        echo "Usage: $0 [test|production]"
        exit 1
        ;;
esac

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_status "Stopping current services..."
systemctl stop checkin-taylaibui-test 2>/dev/null || echo "Test service not running"
systemctl stop checkin-taylaibui 2>/dev/null || echo "Production service not running"
pkill -f gunicorn 2>/dev/null || echo "No gunicorn processes"

print_status "Updating code from Git..."
cd $PROJECT_DIR

# Fix Git ownership
git config --global --add safe.directory $PROJECT_DIR

# Backup current .env
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d-%H%M%S)
fi

# Pull latest code
git stash 2>/dev/null || echo "Nothing to stash"
git pull origin master

# Set proper ownership
chown -R www-data:www-data $PROJECT_DIR

print_status "Installing/updating dependencies..."
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements.txt

print_status "Setting up $ENVIRONMENT environment..."
sudo -u www-data cp "config/${ENVIRONMENT}.env" .env

# Show environment settings
print_status "Environment settings:"
echo "----------------------------------------"
cat .env | grep -E "^(DJANGO_|DATABASE_|ALLOWED_|DEBUG)" | head -8
echo "----------------------------------------"

print_status "Running Django setup for $ENVIRONMENT..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py check

if [ $? -eq 0 ]; then
    print_success "✅ Django configuration valid"
    
    # Run migrations
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate
    
    # Collect static files
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput
    
    # Create admin user if needed
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@checkin.taylaibui.vn', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️ Admin user already exists')
"
    
else
    print_error "❌ Django configuration error!"
    exit 1
fi

# Setup systemd service
SERVICE_NAME="checkin-taylaibui-${ENVIRONMENT}"
print_status "Setting up systemd service: $SERVICE_NAME..."

if [ "$ENVIRONMENT" = "test" ]; then
    # Test service with debug settings
    tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System - TEST Environment
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=test"
Environment="DJANGO_SECRET_KEY=nov-reco-test-secret-key-for-checkin-taylaibui-vn"
Environment="ALLOWED_HOSTS=checkin.taylaibui.vn,www.checkin.taylaibui.vn,103.15.51.66,localhost,127.0.0.1"
Environment="DJANGO_DEBUG=1"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 project.wsgi:application --timeout 120 --log-level debug
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
else
    # Production service
    tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System - PRODUCTION Environment
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
Environment="DJANGO_SECRET_KEY=nov-reco-production-secret-key-change-this-in-real-production"
Environment="ALLOWED_HOSTS=checkin.taylaibui.vn,www.checkin.taylaibui.vn"
Environment="DJANGO_DEBUG=0"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF
fi

# Setup Nginx
print_status "Setting up Nginx for $ENVIRONMENT..."
NGINX_CONFIG="/etc/nginx/sites-available/checkin.taylaibui.vn"

tee $NGINX_CONFIG > /dev/null << EOF
server {
    listen 80;
    server_name checkin.taylaibui.vn www.checkin.taylaibui.vn 103.15.51.66;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
    }

    location = /favicon.ico {
        alias $PROJECT_DIR/staticfiles/favicon.ico;
        access_log off;
        log_not_found off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/

nginx -t

print_status "Starting services..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME
systemctl restart nginx

# Wait and test
sleep 10

print_status "Testing $ENVIRONMENT deployment..."
echo "Local Django test:"
curl -I http://localhost:8000 2>/dev/null | head -2 || echo "❌ Django not responding"

echo -e "\nWebsite test:"
curl -I http://checkin.taylaibui.vn 2>/dev/null | head -2 || echo "❌ Website not responding"

# Show service status
echo -e "\n=== Service Status ==="
systemctl status $SERVICE_NAME --no-pager -l

print_success "🎉 $ENVIRONMENT environment update completed!"

case $ENVIRONMENT in
    test)
        print_status "🧪 TEST Environment Active"
        print_status "🌐 Website: http://checkin.taylaibui.vn"
        print_status "🔧 Admin: http://checkin.taylaibui.vn/admin/"
        print_status "👤 Login: admin / admin123"
        print_warning "📝 This is TEST environment with DEBUG=True"
        ;;
    production)
        print_status "🌐 PRODUCTION Environment Active"
        print_status "🌐 Website: http://checkin.taylaibui.vn"
        print_status "🔧 Admin: http://checkin.taylaibui.vn/admin/"
        print_warning "🔒 Remember to setup SSL for production!"
        ;;
esac

echo ""
print_status "🔧 Management commands:"
echo "  - Check logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Restart: sudo systemctl restart $SERVICE_NAME"
echo "  - Status: sudo systemctl status $SERVICE_NAME"
