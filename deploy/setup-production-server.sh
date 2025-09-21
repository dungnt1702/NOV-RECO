#!/bin/bash
# Production Server Setup Script for checkin.taylaibui.vn
# This script sets up the NOV-RECO system on a production server

set -e

echo "🚀 Setting up NOV-RECO for production server..."

# Configuration
PROJECT_DIR="/var/www/checkin.taylaibui.vn"
USER="www-data"
DOMAIN="checkin.taylaibui.vn"

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

print_status "Creating project directory..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/data

print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx git

print_status "Setting up Python environment..."
cd $PROJECT_DIR
python3 -m venv venv
chown -R $USER:$USER $PROJECT_DIR

print_status "Installing Python dependencies..."
sudo -u $USER $PROJECT_DIR/venv/bin/pip install --upgrade pip
sudo -u $USER $PROJECT_DIR/venv/bin/pip install -r requirements.txt

print_status "Setting up environment variables..."
sudo -u $USER cp config/production.env .env

print_status "Running Django setup..."
cd $PROJECT_DIR
sudo -u $USER DJANGO_ENVIRONMENT=production $PROJECT_DIR/venv/bin/python manage.py migrate
sudo -u $USER DJANGO_ENVIRONMENT=production $PROJECT_DIR/venv/bin/python manage.py collectstatic --noinput

print_status "Creating admin user..."
sudo -u $USER DJANGO_ENVIRONMENT=production $PROJECT_DIR/venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin123')
    print('Admin user created: admin/admin123')
"

print_status "Setting up systemd service..."
tee /etc/systemd/system/checkin-taylaibui.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System - $DOMAIN
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
Environment="DJANGO_SECRET_KEY=nov-reco-production-secret-key-change-this"
Environment="ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx..."
tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
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

ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

print_status "Starting services..."
systemctl daemon-reload
systemctl enable checkin-taylaibui
systemctl start checkin-taylaibui
systemctl restart nginx

print_success "🎉 NOV-RECO deployment completed!"
print_status "🌐 Application URL: http://$DOMAIN"
print_status "🔧 Admin panel: http://$DOMAIN/admin/"
print_status "👤 Default login: admin / admin123"

print_warning "📝 Next steps:"
print_warning "1. Change admin password"
print_warning "2. Update DJANGO_SECRET_KEY in systemd service"
print_warning "3. Set up SSL certificate"

echo "✅ Check service status: systemctl status checkin-taylaibui"
