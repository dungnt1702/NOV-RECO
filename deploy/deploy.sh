#!/bin/bash
# Production Deployment Script for NOV-RECO Check-in System

set -e  # Exit on any error

echo "🚀 Starting NOV-RECO Check-in System Deployment..."

# Configuration
PROJECT_NAME="nov-reco-checkin"
PROJECT_DIR="/var/www/nov-reco"
PYTHON_VERSION="3.12"
USER="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_status "Setting up project directory..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
chown -R $USER:$USER $PROJECT_DIR

print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

print_status "Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-production.txt

print_status "Setting up PostgreSQL database..."
sudo -u postgres createdb $DATABASE_NAME 2>/dev/null || print_warning "Database already exists"
sudo -u postgres createuser $DATABASE_USER 2>/dev/null || print_warning "User already exists"
sudo -u postgres psql -c "ALTER USER $DATABASE_USER PASSWORD '$DATABASE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DATABASE_USER;"

print_status "Running Django setup..."
python manage.py collectstatic --noinput
python manage.py migrate

print_status "Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@nov-reco.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

print_status "Setting up Gunicorn service..."
cat > /etc/systemd/system/nov-reco.service << EOF
[Unit]
Description=NOV-RECO Check-in System
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/config/production.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx configuration..."
cat > /etc/nginx/sites-available/nov-reco << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
    }
    
    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://localhost:8000;
    }
}
EOF

ln -sf /etc/nginx/sites-available/nov-reco /etc/nginx/sites-enabled/
nginx -t

print_status "Starting services..."
systemctl daemon-reload
systemctl enable nov-reco
systemctl start nov-reco
systemctl restart nginx

print_success "Deployment completed successfully!"
print_status "Service status:"
systemctl status nov-reco --no-pager -l

print_status "🌐 Your application should be available at:"
print_success "http://yourdomain.com (replace with your actual domain)"
print_status "📝 Admin panel: http://yourdomain.com/admin/"
print_status "👤 Default admin: admin / admin123"

print_warning "⚠️  Remember to:"
print_warning "1. Update your domain in /etc/nginx/sites-available/nov-reco"
print_warning "2. Set up SSL certificate (Let's Encrypt recommended)"
print_warning "3. Update environment variables in $PROJECT_DIR/config/production.env"
print_warning "4. Change default admin password"
print_warning "5. Configure Google OAuth if needed"

echo "🎉 Deployment script completed!"
