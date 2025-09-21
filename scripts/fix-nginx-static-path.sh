#!/bin/bash
# Fix Nginx static files path - it's looking in wrong directory

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

print_status "🔧 Fixing Nginx static files path..."

# 1. Show current problem
print_status "=== Current Nginx Config Issue ==="
print_error "Nginx is looking in: /usr/share/nginx/html/static/"
print_error "Should be looking in: /var/www/checkin.taylaibui.vn/staticfiles/"

# 2. Backup current config
print_status "Backing up current Nginx config..."
sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn /etc/nginx/sites-available/checkin.taylaibui.vn.backup.$(date +%Y%m%d-%H%M%S)

# 3. Show current static location config
print_status "Current static location config:"
grep -A 5 "location /static/" /etc/nginx/sites-available/checkin.taylaibui.vn

# 4. Check if there's a conflicting default server
print_status "=== Checking for conflicting servers ==="
print_status "Active Nginx sites:"
ls -la /etc/nginx/sites-enabled/

# 5. Check main nginx.conf for conflicting settings
print_status "Checking main nginx.conf for static handling:"
grep -n "location.*static" /etc/nginx/nginx.conf || echo "No static location in main config"

# 6. Disable default site if it exists
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    print_status "Disabling default Nginx site..."
    sudo rm -f /etc/nginx/sites-enabled/default
    print_success "✅ Default site disabled"
else
    print_status "Default site already disabled"
fi

# 7. Ensure our site is the only one enabled
print_status "Ensuring only our site is enabled..."
sudo rm -f /etc/nginx/sites-enabled/*
sudo ln -sf /etc/nginx/sites-available/checkin.taylaibui.vn /etc/nginx/sites-enabled/

# 8. Test and reload Nginx
print_status "Testing Nginx configuration..."
if sudo nginx -t; then
    print_success "✅ Nginx config valid"
    sudo systemctl reload nginx
    print_success "✅ Nginx reloaded"
else
    print_error "❌ Nginx config invalid!"
    exit 1
fi

# 9. Test static files immediately
sleep 2
print_status "=== Testing static files after fix ==="

for file in "css/home.css" "js/base.js" "logo.svg"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://checkin.taylaibui.vn/static/$file" 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        print_success "✅ /static/$file: HTTP $STATUS"
    else
        print_error "❌ /static/$file: HTTP $STATUS"
    fi
done

# 10. Check Nginx error log for improvements
print_status "Recent Nginx errors after fix:"
tail -5 /var/log/nginx/error.log | grep -E "(static|404)" || echo "No recent static file errors!"

print_status "✅ Nginx static path fix completed!"
