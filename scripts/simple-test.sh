#!/bin/bash
# Simple test script to compare with safe-update results

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

print_status "🧪 Simple test after manual commands..."

# Test the exact same URLs as safe-update script
WEBSITE_URL="http://checkin.taylaibui.vn"
STATIC_URL="http://checkin.taylaibui.vn/static/css/home.css"

print_status "Testing website: $WEBSITE_URL"
WEBSITE_RESPONSE=$(curl -s -I "$WEBSITE_URL" 2>/dev/null)
WEBSITE_STATUS=$(echo "$WEBSITE_RESPONSE" | head -1 | grep -o '[0-9][0-9][0-9]' || echo "000")

print_status "Testing static files: $STATIC_URL"
STATIC_RESPONSE=$(curl -s -I "$STATIC_URL" 2>/dev/null)
STATIC_STATUS=$(echo "$STATIC_RESPONSE" | head -1 | grep -o '[0-9][0-9][0-9]' || echo "000")

print_status "=== Results ==="
print_status "Website: HTTP $WEBSITE_STATUS"
print_status "Static files: HTTP $STATIC_STATUS"

# Show full response headers
print_status "=== Website Response Headers ==="
echo "$WEBSITE_RESPONSE"

print_status "=== Static Files Response Headers ==="
echo "$STATIC_RESPONSE"

# Test Django direct access
print_status "Testing Django direct access..."
DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
print_status "Django localhost:8000: HTTP $DJANGO_STATUS"

# Check if static file actually exists
print_status "Checking if static file exists on filesystem..."
if [ -f "staticfiles/css/home.css" ]; then
    print_success "✅ staticfiles/css/home.css exists"
    ls -la staticfiles/css/home.css
else
    print_error "❌ staticfiles/css/home.css missing"
fi

# Check Nginx config
print_status "Current Nginx config for static files:"
grep -A 10 "location /static/" /etc/nginx/sites-available/checkin.taylaibui.vn || echo "No static location found"

print_status "🎯 Manual test completed!"
