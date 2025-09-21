#!/bin/bash
# Script to diagnose and fix HTTP 301 redirect errors on server

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_status "🔍 Diagnosing HTTP 301 redirect issues..."

# Test direct IP access
print_status "Testing IP access..."
curl -I http://103.15.51.66/ 2>/dev/null | head -3

# Test domain access  
print_status "Testing domain access..."
curl -I http://checkin.taylaibui.vn/ 2>/dev/null | head -3

# Test static files
print_status "Testing static files..."
curl -I http://checkin.taylaibui.vn/static/css/home.css 2>/dev/null | head -3

# Check Django service status
print_status "Checking Django service..."
systemctl is-active checkin-taylaibui-test || print_error "Django service not running"

# Check Nginx config for redirects
print_status "Checking Nginx config for redirects..."
grep -n "return 301\|redirect" /etc/nginx/sites-available/checkin.taylaibui.vn || print_status "No explicit redirects found"

# Check if Django is responding on localhost:8000
print_status "Testing Django direct access..."
curl -I http://localhost:8000/ 2>/dev/null | head -3 || print_error "Django not responding on localhost:8000"

# Check environment settings that might cause redirects
print_status "Checking environment settings..."
cd /var/www/checkin.taylaibui.vn
if [ -f ".env" ]; then
    echo "SECURE_SSL_REDIRECT: $(grep SECURE_SSL_REDIRECT .env || echo 'not set')"
    echo "DJANGO_DEBUG: $(grep DJANGO_DEBUG .env || echo 'not set')"
    echo "ALLOWED_HOSTS: $(grep ALLOWED_HOSTS .env || echo 'not set')"
else
    print_error ".env file not found"
fi

print_status "🔧 Applying fixes..."

# Fix 1: Ensure Django service is running
print_status "Restarting Django service..."
systemctl stop checkin-taylaibui-test
sleep 2
systemctl start checkin-taylaibui-test
sleep 3

# Fix 2: Ensure no SSL redirects in test environment
print_status "Disabling SSL redirects for test environment..."
cd /var/www/checkin.taylaibui.vn
sed -i 's/SECURE_SSL_REDIRECT=1/SECURE_SSL_REDIRECT=0/g' .env 2>/dev/null || true

# Fix 3: Restart services
print_status "Restarting Nginx..."
systemctl reload nginx

# Wait and test again
sleep 5
print_status "🧪 Testing after fixes..."

print_status "Testing website..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/)
if [ "$RESPONSE" = "200" ]; then
    print_success "✅ Website responding with HTTP 200"
else
    print_error "❌ Website still returning HTTP $RESPONSE"
fi

print_status "Testing static files..."
STATIC_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css)
if [ "$STATIC_RESPONSE" = "200" ]; then
    print_success "✅ Static files responding with HTTP 200"
else
    print_error "❌ Static files still returning HTTP $STATIC_RESPONSE"
fi

print_success "🎉 Diagnosis and fix attempt completed!"
