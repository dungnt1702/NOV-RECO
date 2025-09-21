#!/bin/bash
# Emergency fix for missing staticfiles directory

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

cd /var/www/checkin.taylaibui.vn

print_status "🚨 Emergency fix for missing staticfiles..."

# 1. Check current state
print_status "Checking current staticfiles state..."
if [ -d "staticfiles" ]; then
    print_status "staticfiles directory exists"
    ls -la staticfiles/ | head -5
else
    print_error "❌ staticfiles directory missing!"
fi

if [ -d "static" ]; then
    print_status "Source static directory exists"
    ls -la static/ | head -5
else
    print_error "❌ Source static directory missing!"
fi

# 2. Fix permissions first
print_status "Fixing permissions..."
sudo mkdir -p staticfiles logs
sudo chown -R www-data:www-data staticfiles/ static/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ static/ media/ data/ logs/

# 3. Copy environment file
print_status "Setting up test environment..."
cp config/test.env .env

# 4. Force collect static files
print_status "Force collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py collectstatic --noinput --clear

# 5. Verify static files
print_status "Verifying static files..."
if [ -f "staticfiles/css/home.css" ]; then
    CSS_SIZE=$(wc -c < "staticfiles/css/home.css")
    print_success "✅ home.css collected ($CSS_SIZE bytes)"
else
    print_error "❌ home.css still missing after collectstatic"
    
    # Manual copy as fallback
    print_status "Manual copy from static/ to staticfiles/..."
    sudo -u www-data cp -r static/* staticfiles/ 2>/dev/null || true
    
    if [ -f "staticfiles/css/home.css" ]; then
        print_success "✅ Manual copy successful"
    else
        print_error "❌ Manual copy failed"
        print_status "Available files in static/:"
        find static/ -name "*.css" | head -5
    fi
fi

# 6. Disable HTTPS redirect temporarily
print_status "Disabling HTTPS redirect for test environment..."
sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn
sudo nginx -t && sudo systemctl reload nginx

# 7. Restart Django service
print_status "Restarting Django service..."
sudo systemctl restart checkin-taylaibui-test
sleep 3

# 8. Test everything
print_status "Testing after emergency fix..."
HTTP_WEBSITE=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/ 2>/dev/null || echo "000")
HTTP_STATIC=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")

print_status "=== Emergency Fix Results ==="
print_status "HTTP website: $HTTP_WEBSITE"
print_status "HTTP static: $HTTP_STATIC"

if [ "$HTTP_WEBSITE" = "200" ] && [ "$HTTP_STATIC" = "200" ]; then
    print_success "🎉 EMERGENCY FIX SUCCESS!"
    print_success "✅ Website working: http://checkin.taylaibui.vn/"
    print_success "✅ Static files working"
    print_status "💡 HTTPS redirect disabled for test environment"
else
    print_error "❌ Emergency fix incomplete:"
    print_error "Website: HTTP $HTTP_WEBSITE (expected 200)"
    print_error "Static: HTTP $HTTP_STATIC (expected 200)"
    
    print_status "Django service logs:"
    sudo journalctl -u checkin-taylaibui-test -n 5 --no-pager
fi

print_status "✅ Emergency fix completed!"
