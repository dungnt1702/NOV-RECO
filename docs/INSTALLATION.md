# NOV-RECO Installation Guide

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/dungnt1702/NOV-RECO.git
cd NOV-RECO

# Run complete setup
data\scripts\setup_complete_data.bat

# Start server
data\scripts\start_reco_local.bat
```

### Option 2: Manual Installation

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11
- **Python**: 3.8+ (3.11 recommended)
- **XAMPP**: For Apache virtual host (optional)
- **Git**: For version control

### Required Software

#### 1. Python Installation
```bash
# Download from https://www.python.org/downloads/
# ✅ Check "Add Python to PATH" during installation
python --version  # Should show Python 3.x.x
```

#### 2. XAMPP Installation (Optional - for reco.local)
```bash
# Download from https://www.apachefriends.org/
# Install Apache for virtual host setup
```

## 🔧 Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/dungnt1702/NOV-RECO.git
cd NOV-RECO
```

### Step 2: Python Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import django; print(django.get_version())"
```

### Step 3: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional - sample data includes users)
python manage.py createsuperuser
```

### Step 4: Sample Data Setup
```bash
# Setup user groups and permissions
python manage.py setup_user_groups

# Create sample users
python manage.py create_sample_users

# Create sample areas
python manage.py create_sample_areas
```

### Step 5: Start Development Server
```bash
python manage.py runserver 3000
```

**Access**: http://localhost:3000

## 🌐 Virtual Host Setup (reco.local)

### Step 1: Edit Hosts File
```bash
# Open as Administrator
notepad C:\Windows\System32\drivers\etc\hosts

# Add line:
127.0.0.1    reco.local
```

### Step 2: Configure Apache Virtual Host
```bash
# Edit: C:\xampp\apache\conf\extra\httpd-vhosts.conf
# Add:
<VirtualHost *:80>
    ServerName reco.local
    DocumentRoot "C:/xampp/htdocs/checkin.reco.vn"
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/
    
    ErrorLog "logs/reco.local-error.log"
    CustomLog "logs/reco.local-access.log" common
</VirtualHost>
```

### Step 3: Enable Apache Modules
```bash
# Edit: C:\xampp\apache\conf\httpd.conf
# Uncomment these lines:
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
Include conf/extra/httpd-vhosts.conf
```

### Step 4: Restart Apache
- Open XAMPP Control Panel
- Stop and Start Apache service

**Access**: http://reco.local

## 👥 Sample User Accounts

| Role | Username | Password | Employee ID | Permissions |
|------|----------|----------|-------------|-------------|
| 🔴 Super Admin | `superadmin` | `admin123` | SA001 | Full system access |
| 🟡 Manager | `quanly` | `quanly123` | QL001 | View/Edit all data |
| 🟢 Secretary | `thuky` | `thuky123` | TK001 | View/Edit (no user mgmt) |
| 🔵 Employee 1 | `nhanvien1` | `nhanvien123` | NV001 | View/Check-in only |
| 🔵 Employee 2 | `nhanvien2` | `nhanvien123` | NV002 | View/Check-in only |

## 🏢 Sample Areas

- 📍 **Văn phòng Hà Nội** (21.0285, 105.8542) - 200m radius
- 📍 **Chi nhánh TP.HCM** (10.8231, 106.6297) - 150m radius
- 📍 **Nhà máy Bắc Ninh** (21.1861, 106.0763) - 300m radius
- 📍 **Kho hàng Đồng Nai** (10.9472, 107.0946) - 250m radius
- 📍 **Showroom Đà Nẵng** (16.0544, 108.2022) - 100m radius

## 🛠️ Utility Scripts

### Located in: `data/scripts/`

#### `setup_complete_data.bat`
- Complete system setup with all sample data
- Creates users, groups, permissions, and areas
- One-click solution for full environment

#### `start_reco_local.bat`
- Starts Django server on port 3000
- Opens browser to reco.local
- Shows login credentials

## 🔍 Troubleshooting

### Common Issues

#### Python Not Found
```bash
# Solution: Add Python to PATH or use full path
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
```

#### Port 3000 Already in Use
```bash
# Solution: Use different port
python manage.py runserver 3001
```

#### Database Locked Error
```bash
# Solution: Stop Django server before moving database
# Or copy instead of move: copy db.sqlite3 data\db.sqlite3
```

#### Apache Virtual Host Not Working
1. Check hosts file entry
2. Verify Apache modules are enabled
3. Restart Apache service
4. Check error logs: `C:\xampp\apache\logs\error.log`

#### Permission Denied Errors
- Run Command Prompt as Administrator
- Check file permissions
- Ensure Django server is stopped before file operations

### Debug Mode

#### Enable Debug Logging
```python
# In project/settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### Check System Status
```bash
python manage.py check
python manage.py showmigrations
python manage.py collectstatic --dry-run
```

## 📁 Directory Structure After Installation

```
checkin.reco.vn/
├── data/
│   ├── scripts/           # Setup scripts
│   └── db.sqlite3         # Database file
├── static/               # Static files
├── templates/            # HTML templates
├── checkin/             # Main app
├── users/               # User management
├── project/             # Django settings
├── docs/                # Documentation
└── manage.py            # Django management
```

## 🔄 Development Workflow

1. **Daily Start**: `data\scripts\start_reco_local.bat`
2. **Code Changes**: Server auto-reloads
3. **Database Changes**: `python manage.py makemigrations && python manage.py migrate`
4. **Static Files**: `python manage.py collectstatic`
5. **Testing**: Use sample accounts to test features

## 📞 Support

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues
- **Email**: developer@checkin.reco.vn

---

*Installation guide for NOV-RECO Check-in System*
*Last updated: September 19, 2025*
