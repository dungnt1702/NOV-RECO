# 🚀 NOV-RECO Server Deployment Guide

Hướng dẫn deploy NOV-RECO Check-in System lên server với Python 3.6.

## 📋 Yêu cầu

- **Python 3.6+** (đã có trên server)
- **Internet connection** để download packages
- **Port 8000** hoặc port khác available

## 🎯 Quick Setup (Recommended)

### Option 1: Complete Setup Script
```bash
# Clone/download project và chạy:
chmod +x deploy/setup-server-py36.sh
./deploy/setup-server-py36.sh
```

### Option 2: Quick Setup
```bash
# Chạy setup nhanh:
chmod +x deploy/quick-setup.sh
./deploy/quick-setup.sh
```

## 🔧 Manual Setup

Nếu scripts không hoạt động, setup thủ công:

### 1. Install pip3
```bash
curl https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
python3 get-pip.py --user
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install packages
```bash
pip install "Django==3.2.25"
pip install "django-allauth==0.54.0"
pip install "djangorestframework==3.14.0"
pip install "Pillow==8.4.0"
pip install "python-dotenv==0.19.2"
```

### 4. Setup Django
```bash
mkdir -p data logs media staticfiles
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Create admin user
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

## 🚀 Start Server

### After setup script:
```bash
./start_server.sh        # Port 8000
./start_server.sh 8080   # Port 8080
```

### Manual start:
```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## 🌐 Access URLs

- **Website**: http://checkin.taylaibui.vn:8000
- **Admin**: http://checkin.taylaibui.vn:8000/admin
- **Login**: admin/admin123

## 🛠️ Management Commands

### Check status:
```bash
./status_server.sh
```

### Stop server:
```bash
./stop_server.sh
```

### Restart server:
```bash
./stop_server.sh
./start_server.sh
```

## 📊 Update from Git

```bash
# Pull latest changes
git pull origin master

# Activate venv
source venv/bin/activate

# Update database
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart server
./stop_server.sh
./start_server.sh
```

## 🔧 Troubleshooting

### Port issues:
```bash
# Try different ports
./start_server.sh 8080
./start_server.sh 8888
./start_server.sh 3000
```

### Permission issues:
```bash
chmod +x deploy/*.sh
chmod +x *.sh
```

### Package installation issues:
```bash
# Upgrade pip
python -m pip install --upgrade "pip<21.0"

# Install packages one by one
pip install "Django==3.2.25"
# ... (repeat for each package)
```

### Database issues:
```bash
# Reset database
rm -f data/db_test.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📝 Environment Variables

Các biến môi trường được set tự động:

```bash
DJANGO_ENVIRONMENT=test
DJANGO_SECRET_KEY=test-secret-key-[timestamp]
DATABASE_NAME=data/db_test.sqlite3
ALLOWED_HOSTS=checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0
```

## 🎯 Production Notes

- **Database**: Sử dụng SQLite cho test environment
- **Static files**: Served by Django development server
- **Media files**: Stored in `media/` directory
- **Logs**: Stored in `logs/` directory

## 📞 Support

Nếu gặp vấn đề, check:

1. **Python version**: `python3 --version`
2. **Virtual environment**: `which python` (should be in venv)
3. **Packages installed**: `pip list`
4. **Server logs**: Check terminal output
5. **Port availability**: `netstat -tlnp | grep :8000`

---

**🎉 Happy Deploying!** 🚀
