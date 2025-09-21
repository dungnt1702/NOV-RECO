# 🚀 NOV-RECO Quick Reference

## 📍 **Workflow Locations**

### 💻 **Localhost (MacBook - Development)**
```bash
# Start development server
source venv/bin/activate
python manage.py runserver 3000

# Code, test, commit
git add .
git commit -m "Your changes"
git push origin master
```

### 🌐 **Server (103.15.51.66 - Production)**
```bash
# SSH to server
ssh root@103.15.51.66
cd /var/www/checkin.taylaibui.vn

# Safe deployment
sudo ./scripts/backup-server-configs.sh
sudo ./scripts/safe-update-from-git.sh test

# Emergency restore
sudo bash /var/backups/nov-reco/latest/restore.sh
```

## 🎯 **Current Status**

| Environment | URL | Status | Notes |
|------------|-----|---------|-------|
| **Development** | http://localhost:3000 | ✅ Working | Local development |
| **Test Server** | http://103.15.51.66 | ✅ Working | IP access only |
| **Domain** | http://checkin.taylaibui.vn | ⏳ Pending | Domain routing issue |
| **HTTPS** | https://checkin.taylaibui.vn | ⏳ Pending | SSL setup needed |

## 📋 **Commands Cheat Sheet**

### Development (Localhost):
```bash
# Start server
source venv/bin/activate && python manage.py runserver 3000

# Switch environment
./scripts/switch-environment.sh local

# Git workflow
git add . && git commit -m "message" && git push origin master
```

### Server Management (103.15.51.66):
```bash
# Backup & Update
sudo ./scripts/backup-server-configs.sh
sudo ./scripts/safe-update-from-git.sh test

# Service control
sudo systemctl restart checkin-taylaibui-test nginx
sudo systemctl status checkin-taylaibui-test

# Logs
sudo journalctl -u checkin-taylaibui-test -f

# Test
curl -I http://103.15.51.66
curl -I http://103.15.51.66/static/css/home.css
```

## 🆘 **Emergency Commands**

```bash
# If deployment fails
sudo bash /var/backups/nov-reco/latest/restore.sh
sudo systemctl restart checkin-taylaibui-test nginx

# If Git conflicts
git stash && git reset --hard origin/master
sudo bash /var/backups/nov-reco/latest/restore.sh

# Check what's running
ps aux | grep python
sudo netstat -tulpn | grep :8000
```

## 🔧 **File Locations**

```
Server (103.15.51.66):
├── /var/www/checkin.taylaibui.vn/          # Project root
├── /var/backups/nov-reco/                  # Backups
├── /etc/nginx/sites-available/checkin.taylaibui.vn  # Nginx config
├── /etc/systemd/system/checkin-taylaibui-test.service  # Service
└── /etc/ssl/certs/taylaibui.vn/            # SSL certificates

Localhost (MacBook):
├── ~/...NOV-RECO/checkin_project/          # Project root
├── config/local.env                        # Local environment
└── scripts/switch-environment.sh           # Environment switcher
```

## 🎯 **Next Steps**

1. **Fix Domain**: Make checkin.taylaibui.vn work
2. **Setup SSL**: Enable HTTPS
3. **Production Server**: Deploy to reco.qly.vn

## 📞 **Quick Help**

- **Server IP**: 103.15.51.66
- **SSH**: `ssh root@103.15.51.66`
- **Project**: `/var/www/checkin.taylaibui.vn`
- **Service**: `checkin-taylaibui-test`
- **Backup**: `/var/backups/nov-reco/latest`
