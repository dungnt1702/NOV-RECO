#!/bin/bash
# Force update script to fix mobile cards on server

set -e

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

if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_status "🚀 Force updating mobile cards on server..."

cd "$PROJECT_DIR"

# 1. Fix permissions first (before stopping service)
print_status "Fixing permissions first..."
sudo mkdir -p logs data staticfiles media
sudo chown -R www-data:www-data logs/ data/ staticfiles/ media/
sudo chmod -R 755 logs/ data/ staticfiles/ media/
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 2. Stop service
print_status "Stopping Django service..."
sudo systemctl stop checkin-taylaibui-test

# 3. Pull latest code
print_status "Pulling latest code..."
git stash || true
git pull origin master

# 4. Copy environment
print_status "Setting test environment..."
cp config/test.env .env

# 5. Force clear all static files and rebuild
print_status "Force clearing and rebuilding static files..."
sudo rm -rf staticfiles/*
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py collectstatic --noinput

# 6. Verify critical CSS files exist and have content
print_status "Verifying CSS files..."
for css_file in "staticfiles/css/base.css" "staticfiles/css/checkin_list.css"; do
    if [ -f "$css_file" ]; then
        size=$(wc -c < "$css_file")
        if [ "$size" -gt 1000 ]; then
            print_success "✅ $css_file ($size bytes)"
        else
            print_error "❌ $css_file too small ($size bytes)"
        fi
    else
        print_error "❌ $css_file missing"
    fi
done

# 7. Verify JavaScript files
print_status "Verifying JS files..."
for js_file in "staticfiles/js/base.js" "staticfiles/js/checkin_list.js"; do
    if [ -f "$js_file" ]; then
        size=$(wc -c < "$js_file")
        if [ "$size" -gt 1000 ]; then
            print_success "✅ $js_file ($size bytes)"
        else
            print_error "❌ $js_file too small ($size bytes)"
        fi
    else
        print_error "❌ $js_file missing"
    fi
done

# 8. Check mobile cards CSS specifically
print_status "Checking mobile cards CSS..."
if grep -q "mobile-card" staticfiles/css/checkin_list.css; then
    print_success "✅ Mobile cards CSS found in checkin_list.css"
else
    print_error "❌ Mobile cards CSS missing from checkin_list.css"
fi

# 9. Fix permissions again after collectstatic
print_status "Fixing permissions after collectstatic..."
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true
sudo chmod 666 logs/django.log 2>/dev/null || true

# 10. Start service
print_status "Starting Django service..."
sudo systemctl start checkin-taylaibui-test

# 10. Wait for service to be ready
sleep 5

# 11. Test service status
if systemctl is-active --quiet checkin-taylaibui-test; then
    print_success "✅ Django service is running"
else
    print_error "❌ Django service failed to start"
    sudo journalctl -u checkin-taylaibui-test -n 10 --no-pager
    exit 1
fi

# 12. Test website
print_status "Testing website..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://checkin.taylaibui.vn" 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "301" ]; then
    print_success "✅ Website responding (HTTP $RESPONSE)"
else
    print_error "❌ Website not responding (HTTP $RESPONSE)"
fi

# 13. Test static files
print_status "Testing static files..."
CSS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://checkin.taylaibui.vn/static/css/checkin_list.css" 2>/dev/null || echo "000")
JS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://checkin.taylaibui.vn/static/js/checkin_list.js" 2>/dev/null || echo "000")

if [ "$CSS_RESPONSE" = "200" ] || [ "$CSS_RESPONSE" = "301" ]; then
    print_success "✅ CSS files accessible (HTTP $CSS_RESPONSE)"
else
    print_error "❌ CSS files not accessible (HTTP $CSS_RESPONSE)"
fi

if [ "$JS_RESPONSE" = "200" ] || [ "$JS_RESPONSE" = "301" ]; then
    print_success "✅ JS files accessible (HTTP $JS_RESPONSE)"
else
    print_error "❌ JS files not accessible (HTTP $JS_RESPONSE)"
fi

print_success "🎉 Force update completed!"
print_status "📱 Test mobile cards: https://checkin.taylaibui.vn/checkin/list-view/"
print_status "🔍 Check console logs for debug output"
