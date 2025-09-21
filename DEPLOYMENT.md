# 🚀 NOV-RECO Check-in System - Deployment Guide

## 📋 Tổng quan

Dự án NOV-RECO được thiết kế với **3 môi trường riêng biệt** để phát triển và triển khai an toàn:

### 🏠 **Local Development** (Bryan's MacBook)
- **URL**: http://localhost:3000
- **Environment**: `local` (DEBUG=True, SQLite)
- **Database**: `data/db_local.sqlite3`
- **Mục đích**: Phát triển và test trên máy local

### 🧪 **Test Server** (checkin.taylaibui.vn)
- **URL**: http://checkin.taylaibui.vn
- **Server IP**: 103.15.51.66
- **Environment**: `test` (DEBUG=True, SQLite)
- **Database**: `data/db_test.sqlite3`
- **Mục đích**: Test trên server thực, staging environment

### 🌐 **Production Server** (reco.qly.vn)
- **URL**: https://reco.qly.vn
- **Environment**: `production` (DEBUG=False, PostgreSQL)
- **Database**: PostgreSQL production database
- **Mục đích**: Production environment cho end users

## 🚀 Quick Start Commands

### 🏠 Local Development (Bryan's MacBook)
```bash
# Switch to local environment
./scripts/switch-environment.sh local

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 3000
```
**URL**: http://localhost:3000

### 🧪 Test Server Deployment (checkin.taylaibui.vn)
```bash
# On server checkin.taylaibui.vn (103.15.51.66)
cd /var/www/checkin.taylaibui.vn
git pull origin master
sudo ./deploy/deploy-test-server.sh
```
**URL**: http://checkin.taylaibui.vn

### 🌐 Production Server Deployment (reco.qly.vn)
```bash
# On production server reco.qly.vn
git clone https://github.com/dungnt1702/NOV-RECO.git /var/www/reco.qly.vn
cd /var/www/reco.qly.vn
sudo ./deploy/deploy-production-reco-qly.sh
```
**URL**: https://reco.qly.vn

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

## ⚙️ Environment Management

### 🔧 Environment Switcher
```bash
# Switch between environments locally
./scripts/switch-environment.sh [local|test|production]

# Examples:
./scripts/switch-environment.sh local      # For localhost development
./scripts/switch-environment.sh test       # For test server config  
./scripts/switch-environment.sh production # For production config
```

### 📁 Environment Configurations

#### 🏠 Local Development (`config/local.env`)
- `DJANGO_DEBUG=1`
- `SERVER_PORT=3000` 
- `DATABASE_NAME=data/db_local.sqlite3`
- Console email backend
- Relaxed security settings
- **URL**: http://localhost:3000

#### 🧪 Test Server (`config/test.env`)
- `DJANGO_DEBUG=1` (for detailed error messages)
- `SERVER_PORT=8000`
- `DATABASE_NAME=/var/www/checkin.taylaibui.vn/data/db_test.sqlite3`
- Console email backend
- Relaxed security for testing
- **URL**: http://checkin.taylaibui.vn

#### 🌐 Production Server (`config/production-reco-qly.env`)
- `DJANGO_DEBUG=0`
- `SERVER_PORT=8000`
- PostgreSQL database
- SMTP email backend
- Strict security settings
- SSL required
- **URL**: https://reco.qly.vn

## 🔧 Configuration Files

```
config/
├── local.env                    # Local development (localhost:3000)
├── test.env                     # Test server (checkin.taylaibui.vn)
├── production.env               # Legacy production config
└── production-reco-qly.env      # Production server (reco.qly.vn)

deploy/
├── deploy-test-server.sh        # Test server deployment
├── deploy-production-reco-qly.sh # Production server deployment
├── deploy.sh                    # Legacy deployment
└── deploy-simple.sh             # Legacy simple deployment

scripts/
├── switch-environment.sh        # Switch between environments
├── update-server-from-git.sh    # Update server from Git
├── manage-environments.sh       # Environment management commands
├── run-local.sh                 # Local development runner
└── run-production.sh            # Legacy production runner
```

## 🚀 Environment Management Commands

### 🔧 Environment Switcher
```bash
# Switch environment configuration locally
./scripts/switch-environment.sh [local|test|production]

# Environment management
./scripts/manage-environments.sh help              # Show all commands
./scripts/manage-environments.sh deploy test       # Deploy to test server
./scripts/manage-environments.sh deploy production # Deploy to production
./scripts/manage-environments.sh status test       # Check test server status
./scripts/manage-environments.sh logs test         # View test server logs
```

### 🏠 Local Development Commands
```bash
./scripts/switch-environment.sh local
python manage.py runserver 3000
# → http://localhost:3000
```

### 🧪 Test Server Commands
```bash
# On checkin.taylaibui.vn server:
sudo ./deploy/deploy-test-server.sh
# → http://checkin.taylaibui.vn
```

### 🌐 Production Server Commands
```bash
# On reco.qly.vn server:
sudo ./deploy/deploy-production-reco-qly.sh
# → https://reco.qly.vn
```

## 🔐 Security Checklist

### 🧪 Test Server Setup (checkin.taylaibui.vn):
- [x] Domain configured: checkin.taylaibui.vn → 103.15.51.66
- [x] SSL certificate uploaded
- [ ] Test all functionality
- [ ] Verify user roles and permissions
- [ ] Test check-in features

### 🌐 Production Server Setup (reco.qly.vn):
- [ ] Configure DNS: reco.qly.vn → production server IP
- [ ] Change `DJANGO_SECRET_KEY` in production-reco-qly.env
- [ ] Update database credentials
- [ ] Change default admin password
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure SMTP email settings
- [ ] Set up Google OAuth credentials
- [ ] Configure firewall rules
- [ ] Setup monitoring and backups

## 📊 Service Management

### 🧪 Test Server (checkin.taylaibui.vn):
```bash
# Check status
sudo systemctl status checkin-taylaibui-test
sudo systemctl status nginx

# Restart services
sudo systemctl restart checkin-taylaibui-test
sudo systemctl restart nginx

# View logs
sudo journalctl -u checkin-taylaibui-test -f
sudo tail -f /var/log/nginx/error.log

# Update from Git
sudo ./scripts/update-server-from-git.sh test
```

### 🌐 Production Server (reco.qly.vn):
```bash
# Check status
sudo systemctl status reco-qly-production
sudo systemctl status nginx

# Restart services
sudo systemctl restart reco-qly-production
sudo systemctl restart nginx

# View logs
sudo journalctl -u reco-qly-production -f
sudo tail -f /var/log/nginx/access.log

# Update from Git
sudo ./scripts/update-server-from-git.sh production
```

## 🌐 Environment URLs

| Environment | URL | Purpose | Status |
|-------------|-----|---------|--------|
| 🏠 **Local** | http://localhost:3000 | Development on MacBook | ✅ Active |
| 🧪 **Test** | http://checkin.taylaibui.vn | Testing on server | 🔄 Setup in progress |
| 🌐 **Production** | https://reco.qly.vn | Live production | ⏳ Future deployment |

## 🎯 Features

- ✅ **3-tier environment system**
- ✅ **Zero-config local development**
- ✅ **One-command server deployment**
- ✅ **Automatic database setup**
- ✅ **SSL-ready configuration**
- ✅ **Multi-environment support**
- ✅ **Systemd service integration**
- ✅ **Nginx reverse proxy**
- ✅ **Static files optimization**
- ✅ **Git-based deployment workflow**

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
