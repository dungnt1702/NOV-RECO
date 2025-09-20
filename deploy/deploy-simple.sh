#!/bin/bash
# Simple Production Deployment Script (SQLite + Gunicorn)
# For servers where you don't want to install PostgreSQL

set -e

echo "🚀 Starting Simple NOV-RECO Deployment..."

# Configuration
PROJECT_DIR="/var/www/nov-reco"
USER="www-data"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

print_status "Creating project directory..."
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p $PROJECT_DIR/logs
sudo mkdir -p $PROJECT_DIR/data

print_status "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx

print_status "Setting up Python environment..."
cd $PROJECT_DIR
sudo python3 -m venv venv
sudo chown -R $USER:$USER $PROJECT_DIR

print_status "Copying project files..."
# Assume project files are in current directory
sudo cp -r . $PROJECT_DIR/
sudo chown -R $USER:$USER $PROJECT_DIR

print_status "Installing Python dependencies..."
sudo -u $USER $PROJECT_DIR/venv/bin/pip install --upgrade pip
sudo -u $USER $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements.txt
sudo -u $USER $PROJECT_DIR/venv/bin/pip install gunicorn whitenoise

print_status "Setting up environment variables..."
sudo -u $USER cp $PROJECT_DIR/config/production.env $PROJECT_DIR/.env

print_status "Running Django setup..."
cd $PROJECT_DIR
sudo -u $USER $PROJECT_DIR/venv/bin/python manage.py collectstatic --noinput
sudo -u $USER $PROJECT_DIR/venv/bin/python manage.py migrate

print_status "Creating admin user..."
sudo -u $USER $PROJECT_DIR/venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@nov-reco.com', 'admin123')
    print('Admin user created: admin/admin123')
"

print_status "Setting up systemd service..."
sudo tee /etc/systemd/system/nov-reco.service > /dev/null << EOF
[Unit]
Description=NOV-RECO Check-in System
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="DJANGO_ENVIRONMENT=production"
Environment="DJANGO_SECRET_KEY=change-this-in-production"
Environment="ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

print_status "Setting up Nginx..."
sudo tee /etc/nginx/sites-available/nov-reco > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
        alias $PROJECT_DIR/static/favicon.ico;
    }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/nov-reco /etc/nginx/sites-enabled/
sudo nginx -t

print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable nov-reco
sudo systemctl start nov-reco
sudo systemctl restart nginx

print_success "🎉 Deployment completed!"
print_status "🌐 Application URL: http://yourdomain.com"
print_status "🔧 Admin panel: http://yourdomain.com/admin/"
print_status "👤 Default login: admin / admin123"

print_warning "📝 Next steps:"
print_warning "1. Update domain in /etc/nginx/sites-available/nov-reco"
print_warning "2. Update environment variables in /etc/systemd/system/nov-reco.service"
print_warning "3. Change admin password"
print_warning "4. Set up SSL certificate (certbot recommended)"

echo "✅ Check service status: sudo systemctl status nov-reco"
