# 🚀 NOV-RECO Check-in System - Deployment Guide

## 📋 Tổng quan

Dự án này được cấu hình để chạy trên cả **Local Development** và **Production** mà không cần cài đặt gì thêm.

## 🏠 Local Development

### Cách 1: Sử dụng script tự động
```bash
# Chạy local development server
./scripts/run-local.sh
```

### Cách 2: Manual setup
```bash
# Set environment variables
export DJANGO_ENVIRONMENT=local
export SERVER_PORT=3000

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver 3000
```

**URL**: http://localhost:3000

## 🧪 Test/Staging Environment

### Cách 1: Local test với full data
```bash
# Chạy test environment với dữ liệu mẫu đầy đủ
./scripts/run-test.sh
```

### Cách 2: Deploy test environment lên server
```bash
# Upload code to test server
scp -r . user@test-server:/tmp/nov-reco-test

# SSH to server and deploy
ssh user@test-server
cd /tmp/nov-reco-test
sudo ./deploy/deploy-test.sh

# Setup SSL certificate (after DNS is configured)
sudo ./deploy/setup-ssl.sh
```

**URL**: http://localhost:8000 (local) hoặc https://checkin.taylaibui.vn (server)

## 🌐 Production Deployment

### Option 1: Automatic Deployment (Recommended)
```bash
# Upload code to server
scp -r . user@your-server:/tmp/nov-reco-checkin

# SSH to server and run deployment
ssh user@your-server
cd /tmp/nov-reco-checkin
sudo ./deploy/deploy-simple.sh
```

### Option 2: Manual Production Setup
```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx

# 2. Setup project
sudo mkdir -p /var/www/nov-reco
sudo cp -r . /var/www/nov-reco/
cd /var/www/nov-reco

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt

# 4. Configure environment
export DJANGO_ENVIRONMENT=production
export DJANGO_SECRET_KEY=your-secret-key
export ALLOWED_HOSTS=yourdomain.com

# 5. Setup Django
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 6. Start with Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 project.wsgi:application
```

## 🗄️ Database Options

### SQLite (Default - Simple)
```bash
# Local
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=data/db.sqlite3

# Production
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=/var/www/nov-reco/data/db.sqlite3
```

### PostgreSQL (Recommended for Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb nov_reco_checkin_prod
sudo -u postgres createuser nov_reco_user
sudo -u postgres psql -c "ALTER USER nov_reco_user PASSWORD 'your-password';"

# Environment variables
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nov_reco_checkin_prod
DATABASE_USER=nov_reco_user
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## ⚙️ Environment Variables

### 🏠 Local Development (`config/local.env`)
- `DJANGO_DEBUG=1`
- `SERVER_PORT=3000`
- SQLite database
- Console email backend
- Relaxed security settings

### 🌐 Production (`config/production.env`)
- `DJANGO_DEBUG=0`
- `SERVER_PORT=8000`
- PostgreSQL/SQLite database
- SMTP email backend
- Strict security settings

## 🔧 Configuration Files

```
config/
├── local.env          # Local development settings
└── production.env     # Production settings

deploy/
├── deploy.sh          # Full production deployment (PostgreSQL)
└── deploy-simple.sh   # Simple deployment (SQLite)

scripts/
├── run-local.sh       # Local development runner
└── run-production.sh  # Production runner (for testing)
```

## 🚀 Quick Start Commands

### Local Development:
```bash
./scripts/run-local.sh
# → http://localhost:3000
```

### Production Test:
```bash
./scripts/run-production.sh
# → http://localhost:8000
```

### Production Deployment:
```bash
sudo ./deploy/deploy-simple.sh
# → http://yourdomain.com
```

## 🔐 Security Checklist

### Production Setup:
- [ ] Change `DJANGO_SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Change default admin password
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure proper email settings
- [ ] Set up Google OAuth credentials
- [ ] Configure firewall rules

## 📊 Service Management

### Check status:
```bash
sudo systemctl status nov-reco
sudo systemctl status nginx
```

### Restart services:
```bash
sudo systemctl restart nov-reco
sudo systemctl restart nginx
```

### View logs:
```bash
sudo journalctl -u nov-reco -f
sudo tail -f /var/log/nginx/access.log
```

## 🎯 Features

- ✅ **Zero-config local development**
- ✅ **One-command production deployment**
- ✅ **Automatic database setup**
- ✅ **SSL-ready configuration**
- ✅ **Multi-environment support**
- ✅ **Systemd service integration**
- ✅ **Nginx reverse proxy**
- ✅ **Static files optimization**

## 🆘 Troubleshooting

### Common Issues:

1. **Permission denied**: `sudo chown -R www-data:www-data /var/www/nov-reco`
2. **Port already in use**: `sudo lsof -i :8000`
3. **Static files not loading**: `python manage.py collectstatic --noinput`
4. **Database errors**: Check environment variables in systemd service

### Debug Commands:
```bash
# Check environment
python manage.py shell -c "import os; print(os.environ.get('DJANGO_ENVIRONMENT'))"

# Test database connection
python manage.py dbshell

# Check static files
python manage.py findstatic favicon.ico
```
