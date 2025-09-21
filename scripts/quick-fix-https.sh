#!/bin/bash
# Quick fix for HTTPS static files 404 - disable HTTPS redirect immediately

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

cd /var/www/checkin.taylaibui.vn

print_status "🚨 Quick fix: Disabling HTTPS redirect..."

# 1. Backup current Nginx config
sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn /etc/nginx/sites-available/checkin.taylaibui.vn.backup.$(date +%Y%m%d-%H%M%S)

# 2. Show current config
print_status "Current Nginx config:"
grep -n "return 301" /etc/nginx/sites-available/checkin.taylaibui.vn || echo "No redirects found"

# 3. Disable HTTPS redirect
print_status "Disabling HTTPS redirect..."
sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn

# 4. Show modified config
print_status "Modified Nginx config:"
grep -n "#return 301" /etc/nginx/sites-available/checkin.taylaibui.vn || echo "No commented redirects found"

# 5. Test and reload Nginx
print_status "Testing Nginx config..."
if sudo nginx -t; then
    print_success "✅ Nginx config valid"
    sudo systemctl reload nginx
    print_status "Nginx reloaded"
else
    print_error "❌ Nginx config invalid, restoring backup..."
    sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn.backup.* /etc/nginx/sites-available/checkin.taylaibui.vn
    exit 1
fi

# 6. Wait and test
sleep 3

# 7. Test HTTP access
print_status "Testing HTTP access..."
HTTP_WEBSITE=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/ 2>/dev/null || echo "000")
HTTP_STATIC=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")

print_status "=== Results ==="
print_status "Website: HTTP $HTTP_WEBSITE"
print_status "Static files: HTTP $HTTP_STATIC"

if [ "$HTTP_WEBSITE" = "200" ] && [ "$HTTP_STATIC" = "200" ]; then
    print_success "🎉 SUCCESS! HTTPS redirect disabled"
    print_success "✅ Website: http://checkin.taylaibui.vn/ (HTTP 200)"
    print_success "✅ Static files: HTTP 200"
    print_status "💡 Website now accessible on HTTP only"
    print_status "💡 CSS and JS should load correctly now"
else
    print_error "❌ Still issues:"
    print_error "Website: HTTP $HTTP_WEBSITE (expected 200)"
    print_error "Static: HTTP $HTTP_STATIC (expected 200)"
    
    # Check if staticfiles exist
    print_status "Checking staticfiles directory..."
    if [ -d "staticfiles/css" ]; then
        ls -la staticfiles/css/ | head -3
    else
        print_error "staticfiles/css directory missing!"
        print_status "Running collectstatic..."
        sudo -u www-data DJANGO_ENVIRONMENT=test ./venv/bin/python manage.py collectstatic --noinput
    fi
fi

print_status "✅ Quick fix completed!"
