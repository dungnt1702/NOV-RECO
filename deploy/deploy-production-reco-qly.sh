#!/bin/bash
# Production Deployment Script for reco.qly.vn
# This script deploys NOV-RECO in PRODUCTION mode

set -e

echo "🌐 Deploying NOV-RECO to PRODUCTION (reco.qly.vn)..."

# Configuration
PROJECT_DIR="/var/www/reco.qly.vn"
USER="www-data"
DOMAIN="reco.qly.vn"
ENVIRONMENT="production"

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_status "Creating production directory..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/data

print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git certbot python3-certbot-nginx

print_status "Setting up PostgreSQL database..."
sudo -u postgres createdb nov_reco_checkin_prod 2>/dev/null || print_warning "Database already exists"
sudo -u postgres createuser nov_reco_user 2>/dev/null || print_warning "User already exists"
sudo -u postgres psql -c "ALTER USER nov_reco_user PASSWORD 'secure-database-password-change-this';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nov_reco_checkin_prod TO nov_reco_user;"

print_status "Setting up project files..."
cd $PROJECT_DIR
git config --global --add safe.directory $PROJECT_DIR
chown -R $USER:$USER $PROJECT_DIR

print_status "Setting up Python environment..."
sudo -u $USER python3 -m venv venv
sudo -u $USER ./venv/bin/pip install --upgrade pip
sudo -u $USER ./venv/bin/pip install -r requirements.txt
sudo -u $USER ./venv/bin/pip install psycopg2-binary  # For PostgreSQL

print_status "Setting up PRODUCTION environment..."
sudo -u $USER cp config/production-reco-qly.env .env

print_warning "⚠️  IMPORTANT: Update these settings in .env:"
print_warning "  - DJANGO_SECRET_KEY"
print_warning "  - DATABASE_PASSWORD" 
print_warning "  - EMAIL settings"
print_warning "  - GOOGLE_OAUTH credentials"

print_status "Running Django setup for PRODUCTION..."
sudo -u $USER DJANGO_ENVIRONMENT=production ./venv/bin/python manage.py migrate
sudo -u $USER DJANGO_ENVIRONMENT=production ./venv/bin/python manage.py collectstatic --noinput

print_status "Creating production admin user..."
sudo -u $USER DJANGO_ENVIRONMENT=production ./venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin123')
    print('✅ Production admin user created: admin/admin123')
    print('⚠️  CHANGE THIS PASSWORD IMMEDIATELY!')
else:
    print('ℹ️ Admin user already exists')
"

print_status "Setting up systemd service for PRODUCTION..."
tee /etc/systemd/system/reco-qly-production.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System - PRODUCTION (reco.qly.vn)
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
Environment="DJANGO_SECRET_KEY=nov-reco-production-secret-key-for-reco-qly-vn-change-this"
Environment="ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN"
Environment="DJANGO_DEBUG=0"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx for PRODUCTION..."
tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server (SSL will be added by certbot)
server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration will be added by certbot
    
    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
    }

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
EOF

# Enable production site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test Nginx config (without SSL first)
sed -i 's/listen 443 ssl/listen 443/' /etc/nginx/sites-available/$DOMAIN
nginx -t

print_status "Starting PRODUCTION services..."
systemctl daemon-reload
systemctl enable reco-qly-production
systemctl start reco-qly-production
systemctl restart nginx

# Wait for services
sleep 10

print_status "Setting up SSL certificate..."
print_warning "📝 SSL Setup - Run these commands after DNS is configured:"
echo "  sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "  sudo systemctl restart nginx"

print_success "🎉 PRODUCTION Environment setup completed!"
print_status "🌐 Website: http://$DOMAIN (will redirect to HTTPS after SSL)"
print_status "🔧 Admin panel: https://$DOMAIN/admin/"
print_status "👤 Default login: admin / admin123"

print_error "🚨 CRITICAL: Change admin password immediately!"
print_warning "📝 Production checklist:"
print_warning "  1. Change admin password"
print_warning "  2. Update DJANGO_SECRET_KEY in .env"
print_warning "  3. Configure database password"
print_warning "  4. Setup SSL certificate"
print_warning "  5. Configure email settings"
print_warning "  6. Setup monitoring"

echo ""
print_status "🔧 Service management:"
echo "  - Status: sudo systemctl status reco-qly-production"
echo "  - Logs: sudo journalctl -u reco-qly-production -f"
echo "  - Restart: sudo systemctl restart reco-qly-production"
