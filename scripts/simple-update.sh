#!/bin/bash
# Simple update script - matches working manual commands

set -e

ENVIRONMENT=$1
PROJECT_DIR="/var/www/checkin.taylaibui.vn"

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 [test|production]"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_status "🚀 Simple update for $ENVIRONMENT environment..."

cd "$PROJECT_DIR"

# 1. Pull latest code
print_status "Pulling latest code..."
git stash || true
git pull origin master

# 2. Copy environment file
print_status "Setting environment..."
cp "config/$ENVIRONMENT.env" ".env"

# 3. Install dependencies
print_status "Installing dependencies..."
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# 4. Fix permissions
print_status "Fixing permissions..."
sudo mkdir -p staticfiles logs media data
sudo chown -R www-data:www-data staticfiles/ static/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ static/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 5. Run migrations
print_status "Running migrations..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate

# 6. Collect static files (exactly like working manual command)
print_status "Collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput

# 7. Restart service (exactly like working manual command)
print_status "Restarting service..."
if [ "$ENVIRONMENT" == "test" ]; then
    sudo systemctl restart checkin-taylaibui-test
elif [ "$ENVIRONMENT" == "production" ]; then
    sudo systemctl restart reco-qly-production
fi

# 8. Simple test
sleep 3
if [ "$ENVIRONMENT" == "test" ]; then
    TEST_URL="http://checkin.taylaibui.vn"
else
    TEST_URL="http://reco.qly.vn"
fi

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_URL" 2>/dev/null || echo "000")
print_status "Website test: $TEST_URL -> HTTP $STATUS"

if [ "$STATUS" = "200" ] || [ "$STATUS" = "301" ]; then
    print_success "🎉 SUCCESS! Simple update completed!"
else
    print_error "❌ Website test failed (HTTP $STATUS)"
fi

print_status "✅ Simple update script completed!"
