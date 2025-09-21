#!/bin/bash
# Safe Git update script that preserves static files

set -e

ENVIRONMENT=$1
PROJECT_DIR="/var/www/checkin.taylaibui.vn"

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 [test|production]"
    exit 1
fi

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

cd "$PROJECT_DIR"

# Error handling function
handle_error() {
    print_error "❌ Update failed! Attempting recovery..."
    
    # Try to restore from backup
    if [ -d "/var/backups/nov-reco/latest" ]; then
        print_status "Restoring from backup..."
        sudo bash /var/backups/nov-reco/latest/restore.sh 2>/dev/null || true
    fi
    
    # Restart services
    if [ "$ENVIRONMENT" == "test" ]; then
        sudo systemctl restart checkin-taylaibui-test nginx 2>/dev/null || true
    elif [ "$ENVIRONMENT" == "production" ]; then
        sudo systemctl restart reco-qly-production nginx 2>/dev/null || true
    fi
    
    print_error "Recovery attempted. Please check manually."
    exit 1
}

# Set error trap
trap handle_error ERR

print_status "🚀 Safe updating server for $ENVIRONMENT environment..."

# 1. Backup static files before Git pull
print_status "Backing up static files..."
if [ -d "staticfiles" ]; then
    cp -r staticfiles staticfiles.backup.$(date +%Y%m%d-%H%M%S)
fi

# 2. Stash local changes (excluding database files)
print_status "Stashing local changes..."
git add .
git reset data/*.sqlite3 data/*.db 2>/dev/null || true
git stash || true

# 3. Pull latest code
print_status "Pulling latest code from Git..."
git pull origin master || git pull origin main

# 4. Copy environment file
print_status "Setting up environment for $ENVIRONMENT..."
cp "config/$ENVIRONMENT.env" ".env"

# 5. Install dependencies
print_status "Installing Python dependencies..."
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# 6. Fix permissions FIRST - before any Django operations
print_status "Fixing permissions..."
sudo mkdir -p logs
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true  # Write permissions for database
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 7. Run migrations
print_status "Running database migrations..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate

# 8. Collect static files
print_status "Collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput

# 9. Restore static files from backup if missing
if [ ! -f "staticfiles/css/home.css" ]; then
    print_status "Static files missing, restoring from backup..."
    LATEST_BACKUP=$(ls -t staticfiles.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        sudo -u www-data cp -r "$LATEST_BACKUP"/* staticfiles/ 2>/dev/null || true
        print_status "Restored from $LATEST_BACKUP"
    fi
    
    # Also try to restore from Git backup
    if [ -d "/var/backups/nov-reco/latest/staticfiles.backup" ]; then
        print_status "Restoring from system backup..."
        sudo -u www-data cp -r /var/backups/nov-reco/latest/staticfiles.backup/* staticfiles/ 2>/dev/null || true
    fi
fi

# 9. Fix permissions (including logs) - BEFORE Django operations
print_status "Fixing permissions..."
sudo mkdir -p logs
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true  # Write permissions for database
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 10. Check Django configuration
print_status "Checking Django configuration..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py check

if [ $? -ne 0 ]; then
    print_error "Django configuration error!"
    exit 1
fi

# 10.5. Ensure admin user exists for test environment
if [ "$ENVIRONMENT" == "test" ]; then
    print_status "Ensuring admin user exists for test environment..."
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py shell << 'PYTHON_SCRIPT'
from django.contrib.auth import get_user_model
from users.models import UserRole

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            role=UserRole.ADMIN,
            employee_id='ADMIN001',
            department='IT'
        )
        print("✅ Created admin user: admin / admin123")
    except Exception as e:
        print(f"⚠️  Could not create admin user: {e}")
else:
    print("✅ Admin user already exists")

print(f"📊 Total users in database: {User.objects.count()}")
PYTHON_SCRIPT
fi

# 11. Restart services carefully
print_status "Restarting services..."
if [ "$ENVIRONMENT" == "test" ]; then
    sudo systemctl stop checkin-taylaibui-test
    sleep 2
    sudo systemctl start checkin-taylaibui-test
    sleep 3
    
    # Check if service started successfully
    if ! systemctl is-active --quiet checkin-taylaibui-test; then
        print_error "Django service failed to start!"
        print_status "Checking logs..."
        sudo journalctl -u checkin-taylaibui-test -n 10 --no-pager
        exit 1
    fi
elif [ "$ENVIRONMENT" == "production" ]; then
    sudo systemctl stop reco-qly-production
    sleep 2
    sudo systemctl start reco-qly-production
    sleep 3
    
    if ! systemctl is-active --quiet reco-qly-production; then
        print_error "Django service failed to start!"
        print_status "Checking logs..."
        sudo journalctl -u reco-qly-production -n 10 --no-pager
        exit 1
    fi
fi

sudo systemctl reload nginx

# 12. Wait and test
sleep 5

# 13. Test website
print_status "Testing website..."
if [ "$ENVIRONMENT" == "test" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://103.15.51.66 || echo "000")
    if [ "$HTTP_CODE" == "200" ]; then
        print_success "✅ Website is working: http://103.15.51.66"
    else
        print_error "❌ Website error (HTTP $HTTP_CODE)"
    fi
    
    # Test static files
    CSS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://103.15.51.66/static/css/home.css || echo "000")
    if [ "$CSS_CODE" == "200" ]; then
        print_success "✅ Static files working"
    else
        print_error "❌ Static files error (HTTP $CSS_CODE)"
    fi
fi

print_success "✅ Safe update completed for $ENVIRONMENT environment!"

# Cleanup old backups (keep last 3)
print_status "Cleaning up old backups..."
ls -t staticfiles.backup.* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null || true

print_status "Update completed successfully!"