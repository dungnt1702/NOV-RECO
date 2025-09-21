# 🛡️ Server Deployment Protection Guide

## 📋 Tổng quan

Hướng dẫn này đảm bảo các cấu hình server không bị mất khi update code từ Git.

## 🔒 Protection System

### 1. **Backup System**
```bash
# Backup configurations trước khi update
sudo ./scripts/backup-server-configs.sh
```

### 2. **Safe Update**
```bash
# Update an toàn từ Git
sudo ./scripts/safe-update-from-git.sh test
```

### 3. **Restore if needed**
```bash
# Khôi phục nếu có vấn đề
sudo bash /var/backups/nov-reco/latest/restore.sh
```

## 📁 Files được bảo vệ

### Server Configurations:
- `.env` - Environment variables
- `data/db_test.sqlite3` - Test database
- `media/` - Uploaded files
- `staticfiles/` - Collected static files
- Nginx configuration
- Systemd service configuration
- SSL certificates

### Files không commit:
- `debug_*.sh` - Debug scripts
- `fix_*.sh` - Fix scripts  
- `test_*.sh` - Test scripts
- `*_server_*.sh` - Server-specific scripts
- `nginx-*.conf` - Server Nginx configs
- `systemd-*.service` - Server service configs

## 🚀 Deployment Workflow

### Step 1: Development
```bash
# Code trên localhost
python manage.py runserver 3000
```

### Step 2: Commit Changes
```bash
# Commit code changes (not server configs)
git add .
git commit -m "Feature: Add new functionality"
git push origin master
```

### Step 3: Update Test Server
```bash
# Trên server test (checkin.taylaibui.vn)
cd /var/www/checkin.taylaibui.vn

# Backup trước khi update
sudo ./scripts/backup-server-configs.sh

# Update an toàn
sudo ./scripts/safe-update-from-git.sh test

# Hoặc manual:
sudo git pull origin master
sudo systemctl restart checkin-taylaibui-test nginx
```

### Step 4: Test và Verify
```bash
# Test website
curl -I http://103.15.51.66
curl -I http://103.15.51.66/admin/

# Test static files
curl -I http://103.15.51.66/static/css/home.css
```

## 🆘 Emergency Recovery

### Nếu update bị lỗi:
```bash
# Khôi phục từ backup gần nhất
sudo bash /var/backups/nov-reco/latest/restore.sh

# Restart services
sudo systemctl restart checkin-taylaibui-test nginx
```

### Nếu Git bị conflict:
```bash
# Reset về commit gần nhất
git stash
git reset --hard origin/master

# Khôi phục configs
sudo bash /var/backups/nov-reco/latest/restore.sh
```

## 🔧 Server Management Commands

### Test Server (checkin.taylaibui.vn):
```bash
# Status
sudo systemctl status checkin-taylaibui-test nginx

# Logs
sudo journalctl -u checkin-taylaibui-test -f

# Restart
sudo systemctl restart checkin-taylaibui-test nginx

# Backup
sudo ./scripts/backup-server-configs.sh

# Safe update
sudo ./scripts/safe-update-from-git.sh test
```

## 📊 Backup Schedule

### Manual Backup:
- Trước mỗi lần update Git
- Trước khi thay đổi cấu hình
- Trước khi update dependencies

### Recommended:
```bash
# Tạo cron job backup hàng ngày
echo "0 2 * * * root /var/www/checkin.taylaibui.vn/scripts/backup-server-configs.sh" >> /etc/crontab
```

## 🎯 Best Practices

### ✅ DO:
- Backup trước khi update
- Test trên localhost trước
- Commit code changes, không commit server configs
- Sử dụng safe-update script
- Kiểm tra website sau mỗi update

### ❌ DON'T:
- Update trực tiếp không backup
- Commit .env files với production secrets
- Commit server-specific scripts
- Force push mà không kiểm tra
- Thay đổi server configs trực tiếp trong Git
