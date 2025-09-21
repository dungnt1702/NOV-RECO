#!/bin/bash
# Safe Update from Git Script
# This script safely updates server from Git while preserving configurations

set -e

ENVIRONMENT=${1:-"test"}
PROJECT_DIR="/var/www/checkin.taylaibui.vn"

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

echo "🛡️ Safe update from Git for $ENVIRONMENT environment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

cd $PROJECT_DIR

# Step 1: Backup current configurations
print_status "Step 1: Backing up current configurations..."
./scripts/backup-server-configs.sh

# Step 2: Check Git status
print_status "Step 2: Checking Git repository..."
git config --global --add safe.directory $PROJECT_DIR
git status

# Step 3: Stash local changes (preserve them)
print_status "Step 3: Preserving local changes..."
git stash push -m "Server configs backup $(date)"

# Step 4: Pull latest code
print_status "Step 4: Pulling latest code..."
git pull origin master

if [ $? -ne 0 ]; then
    print_warning "Git pull failed, trying force update..."
    git fetch origin
    git reset --hard origin/master
fi

# Step 5: Restore critical configurations
print_status "Step 5: Restoring critical configurations..."

# Restore .env if it was overwritten
if [ -f "/var/backups/nov-reco/latest/env.backup" ]; then
    if [ ! -f ".env" ] || [ "$(wc -l < .env)" -lt 5 ]; then
        print_warning "Restoring .env from backup..."
        cp /var/backups/nov-reco/latest/env.backup .env
        chown www-data:www-data .env
    fi
fi

# Restore database if needed
if [ -f "/var/backups/nov-reco/latest/db_test.sqlite3.backup" ]; then
    if [ ! -f "data/db_test.sqlite3" ]; then
        print_warning "Restoring database from backup..."
        cp /var/backups/nov-reco/latest/db_test.sqlite3.backup data/db_test.sqlite3
        chown www-data:www-data data/db_test.sqlite3
    fi
fi

# Step 6: Update dependencies
print_status "Step 6: Updating dependencies..."
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# Step 7: Run Django setup
print_status "Step 7: Running Django setup..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py check

if [ $? -eq 0 ]; then
    # Run migrations (safe)
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate
    
    # Collect static files
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput
    
    # Copy additional static files from backup if needed
    if [ -d "/var/backups/nov-reco/latest/staticfiles.backup" ]; then
        print_status "Merging static files from backup..."
        sudo -u www-data cp -r /var/backups/nov-reco/latest/staticfiles.backup/* staticfiles/ 2>/dev/null || true
    fi
    
else
    print_error "Django configuration error!"
    print_warning "Restoring from backup..."
    bash /var/backups/nov-reco/latest/restore.sh
    exit 1
fi

# Step 8: Restart services
print_status "Step 8: Restarting services..."
systemctl restart checkin-taylaibui-test
systemctl restart nginx

# Wait for services
sleep 5

# Step 9: Test website
print_status "Step 9: Testing website..."
if curl -s http://localhost:8000 > /dev/null; then
    print_success "✅ Django server responding"
else
    print_error "❌ Django server not responding"
fi

if curl -s http://103.15.51.66 > /dev/null; then
    print_success "✅ Website accessible via IP"
else
    print_error "❌ Website not accessible via IP"
fi

# Test static files
echo "Testing static files..."
curl -I http://103.15.51.66/static/css/home.css 2>/dev/null | head -2 || echo "⚠️ home.css not found"
curl -I http://103.15.51.66/static/css/base.css 2>/dev/null | head -2 || echo "⚠️ base.css not found"

print_success "🎉 Safe update completed!"
print_status "🌐 Website: http://103.15.51.66"
print_status "🔧 Admin: http://103.15.51.66/admin/"

print_warning "📝 Backup location: /var/backups/nov-reco/latest"
print_warning "🔄 If issues: sudo bash /var/backups/nov-reco/latest/restore.sh"

# Show service status
echo ""
print_status "🔧 Service Status:"
echo "  Django: $(systemctl is-active checkin-taylaibui-test)"
echo "  Nginx: $(systemctl is-active nginx)"

# Show recent backups
echo ""
print_status "📋 Recent Backups:"
ls -la /var/backups/nov-reco/ 2>/dev/null | tail -5 || echo "No backups found"
