#!/bin/bash
# Diagnose static files 404 issue

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

print_status "🔍 Diagnosing static files 404 issue..."

print_status "=== 1. Check staticfiles directory ==="
if [ -d "staticfiles" ]; then
    print_success "✅ staticfiles directory exists"
    ls -la staticfiles/ | head -5
    
    if [ -d "staticfiles/css" ]; then
        print_success "✅ staticfiles/css exists"
        ls -la staticfiles/css/ | head -3
        
        if [ -f "staticfiles/css/home.css" ]; then
            print_success "✅ home.css exists ($(wc -c < staticfiles/css/home.css) bytes)"
        else
            print_error "❌ home.css missing"
        fi
    else
        print_error "❌ staticfiles/css missing"
    fi
else
    print_error "❌ staticfiles directory missing"
fi

print_status "=== 2. Check Nginx static files config ==="
print_status "Nginx static files location:"
grep -A 5 "location /static/" /etc/nginx/sites-available/checkin.taylaibui.vn

print_status "=== 3. Test Nginx static file serving directly ==="
print_status "Testing: curl -I http://127.0.0.1/static/css/home.css"
curl -I http://127.0.0.1/static/css/home.css 2>/dev/null | head -3

print_status "=== 4. Check file permissions ==="
ls -la staticfiles/css/home.css 2>/dev/null || echo "File not found"

print_status "=== 5. Check Nginx error logs ==="
print_status "Recent Nginx errors:"
tail -10 /var/log/nginx/error.log | grep -E "(static|404)" || echo "No recent static file errors"

print_status "=== 6. Test different static file paths ==="
for file in "css/home.css" "js/base.js" "logo.svg"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://checkin.taylaibui.vn/static/$file" 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        print_success "✅ /static/$file: HTTP $STATUS"
    else
        print_error "❌ /static/$file: HTTP $STATUS"
    fi
done

print_status "=== 7. Django STATIC settings ==="
print_status "STATIC_ROOT in Django:"
sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.conf import settings
print('STATIC_ROOT:', settings.STATIC_ROOT)
print('STATIC_URL:', settings.STATIC_URL)
print('STATICFILES_DIRS:', getattr(settings, 'STATICFILES_DIRS', 'Not set'))
"

print_status "✅ Diagnosis completed!"
