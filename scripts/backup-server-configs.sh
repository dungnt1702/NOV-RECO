#!/bin/bash
# Backup Server Configuration Script
# This script backs up important server configurations before Git updates

set -e

PROJECT_DIR="/var/www/checkin.taylaibui.vn"
BACKUP_DIR="/var/backups/nov-reco"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "💾 Backing up server configurations..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create backup directory
print_status "Creating backup directory..."
mkdir -p $BACKUP_DIR/$TIMESTAMP

cd $PROJECT_DIR

# Backup important files
print_status "Backing up configuration files..."

# Backup .env file
if [ -f ".env" ]; then
    cp .env $BACKUP_DIR/$TIMESTAMP/env.backup
    print_success "✅ .env file backed up"
fi

# Backup database
if [ -f "data/db_test.sqlite3" ]; then
    cp data/db_test.sqlite3 $BACKUP_DIR/$TIMESTAMP/db_test.sqlite3.backup
    print_success "✅ Test database backed up"
fi

# Backup media files
if [ -d "media" ]; then
    cp -r media $BACKUP_DIR/$TIMESTAMP/media.backup
    print_success "✅ Media files backed up"
fi

# Backup staticfiles
if [ -d "staticfiles" ]; then
    cp -r staticfiles $BACKUP_DIR/$TIMESTAMP/staticfiles.backup
    print_success "✅ Static files backed up"
fi

# Backup Nginx config
if [ -f "/etc/nginx/sites-available/checkin.taylaibui.vn" ]; then
    cp /etc/nginx/sites-available/checkin.taylaibui.vn $BACKUP_DIR/$TIMESTAMP/nginx.conf.backup
    print_success "✅ Nginx config backed up"
fi

# Backup systemd service
if [ -f "/etc/systemd/system/checkin-taylaibui-test.service" ]; then
    cp /etc/systemd/system/checkin-taylaibui-test.service $BACKUP_DIR/$TIMESTAMP/systemd.service.backup
    print_success "✅ Systemd service backed up"
fi

# Backup SSL certificates
if [ -d "/etc/ssl/certs/taylaibui.vn" ]; then
    cp -r /etc/ssl/certs/taylaibui.vn $BACKUP_DIR/$TIMESTAMP/ssl-certs.backup
    print_success "✅ SSL certificates backed up"
fi

if [ -d "/etc/ssl/private/taylaibui.vn" ]; then
    cp -r /etc/ssl/private/taylaibui.vn $BACKUP_DIR/$TIMESTAMP/ssl-private.backup
    print_success "✅ SSL private keys backed up"
fi

# Create restore script
print_status "Creating restore script..."
tee $BACKUP_DIR/$TIMESTAMP/restore.sh > /dev/null << EOF
#!/bin/bash
# Restore script for backup created on $TIMESTAMP
echo "🔄 Restoring configurations from backup $TIMESTAMP..."

cd $PROJECT_DIR

# Restore .env
if [ -f "$BACKUP_DIR/$TIMESTAMP/env.backup" ]; then
    cp $BACKUP_DIR/$TIMESTAMP/env.backup .env
    chown www-data:www-data .env
    echo "✅ .env restored"
fi

# Restore database
if [ -f "$BACKUP_DIR/$TIMESTAMP/db_test.sqlite3.backup" ]; then
    cp $BACKUP_DIR/$TIMESTAMP/db_test.sqlite3.backup data/db_test.sqlite3
    chown www-data:www-data data/db_test.sqlite3
    echo "✅ Database restored"
fi

# Restore media
if [ -d "$BACKUP_DIR/$TIMESTAMP/media.backup" ]; then
    rm -rf media
    cp -r $BACKUP_DIR/$TIMESTAMP/media.backup media
    chown -R www-data:www-data media
    echo "✅ Media files restored"
fi

# Restore staticfiles
if [ -d "$BACKUP_DIR/$TIMESTAMP/staticfiles.backup" ]; then
    rm -rf staticfiles
    cp -r $BACKUP_DIR/$TIMESTAMP/staticfiles.backup staticfiles
    chown -R www-data:www-data staticfiles
    echo "✅ Static files restored"
fi

# Restore Nginx config
if [ -f "$BACKUP_DIR/$TIMESTAMP/nginx.conf.backup" ]; then
    cp $BACKUP_DIR/$TIMESTAMP/nginx.conf.backup /etc/nginx/sites-available/checkin.taylaibui.vn
    nginx -t && systemctl reload nginx
    echo "✅ Nginx config restored"
fi

# Restore systemd service
if [ -f "$BACKUP_DIR/$TIMESTAMP/systemd.service.backup" ]; then
    cp $BACKUP_DIR/$TIMESTAMP/systemd.service.backup /etc/systemd/system/checkin-taylaibui-test.service
    systemctl daemon-reload
    echo "✅ Systemd service restored"
fi

echo "🎉 Restore completed!"
echo "🔄 Restart services: systemctl restart checkin-taylaibui-test nginx"
EOF

chmod +x $BACKUP_DIR/$TIMESTAMP/restore.sh

# Create info file
tee $BACKUP_DIR/$TIMESTAMP/backup-info.txt > /dev/null << EOF
NOV-RECO Server Backup Information
==================================
Backup Date: $(date)
Server: checkin.taylaibui.vn (103.15.51.66)
Project Directory: $PROJECT_DIR
Backup Directory: $BACKUP_DIR/$TIMESTAMP

Files Backed Up:
- .env (environment variables)
- data/db_test.sqlite3 (test database)
- media/ (uploaded files)
- staticfiles/ (static files)
- Nginx configuration
- Systemd service configuration
- SSL certificates

To Restore:
sudo bash $BACKUP_DIR/$TIMESTAMP/restore.sh

To List Backups:
ls -la $BACKUP_DIR/
EOF

print_success "🎉 Backup completed!"
print_status "📁 Backup location: $BACKUP_DIR/$TIMESTAMP"
print_status "🔄 Restore command: sudo bash $BACKUP_DIR/$TIMESTAMP/restore.sh"

# Show backup contents
echo ""
print_status "📋 Backup contents:"
ls -la $BACKUP_DIR/$TIMESTAMP/

# Create latest symlink
rm -f $BACKUP_DIR/latest
ln -sf $BACKUP_DIR/$TIMESTAMP $BACKUP_DIR/latest

echo ""
print_warning "📝 Important: Run this backup script before each Git update!"
print_warning "💡 Quick backup: sudo ./scripts/backup-server-configs.sh"
