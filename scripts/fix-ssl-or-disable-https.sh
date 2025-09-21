#!/bin/bash
# Fix SSL certificate or temporarily disable HTTPS redirect

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

print_status "🔧 Fixing HTTPS static files 404 errors..."

# Test current HTTPS status
print_status "Testing HTTPS connection..."
HTTPS_TEST=$(curl -s -I https://checkin.taylaibui.vn/ 2>&1 || echo "failed")

if echo "$HTTPS_TEST" | grep -q "SSL\|certificate\|connection refused"; then
    print_error "❌ HTTPS connection failed - SSL certificate issue"
    print_status "$HTTPS_TEST"
    
    print_status "🔧 Option 1: Temporarily disable HTTPS redirect for test environment"
    print_status "This will allow website to work on HTTP until SSL is fixed"
    
    # Backup current Nginx config
    sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn /etc/nginx/sites-available/checkin.taylaibui.vn.backup.$(date +%Y%m%d-%H%M%S)
    
    # Comment out SSL redirect
    sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn
    
    # Test Nginx config
    if sudo nginx -t; then
        print_status "Nginx config valid, reloading..."
        sudo systemctl reload nginx
        sleep 2
        
        # Test HTTP access after disabling redirect
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/ 2>/dev/null || echo "000")
        STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")
        
        if [ "$HTTP_STATUS" = "200" ] && [ "$STATIC_STATUS" = "200" ]; then
            print_success "✅ SUCCESS! Website now working on HTTP"
            print_success "✅ Website: http://checkin.taylaibui.vn/ (HTTP $HTTP_STATUS)"
            print_success "✅ Static files: HTTP $STATIC_STATUS"
            print_status "💡 HTTPS redirect disabled for test environment"
            print_status "💡 To re-enable HTTPS, fix SSL certificate and restore Nginx config"
        else
            print_error "❌ Still issues after disabling HTTPS redirect"
            print_error "Website: HTTP $HTTP_STATUS, Static: HTTP $STATIC_STATUS"
        fi
    else
        print_error "❌ Nginx config error, restoring backup..."
        sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn.backup.$(date +%Y%m%d)* /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null || true
        sudo systemctl reload nginx
    fi
    
else
    print_success "✅ HTTPS connection working"
    print_status "Testing HTTPS static files..."
    
    HTTPS_STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")
    
    if [ "$HTTPS_STATIC_STATUS" = "200" ]; then
        print_success "✅ HTTPS static files working"
    else
        print_error "❌ HTTPS static files not working (HTTP $HTTPS_STATIC_STATUS)"
        print_status "Checking static files directory..."
        ls -la staticfiles/css/ | head -5
    fi
fi

print_status "🎯 Current status summary:"
print_status "HTTP website: $(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/ 2>/dev/null || echo "000")"
print_status "HTTP static: $(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")"
print_status "HTTPS website: $(curl -s -o /dev/null -w "%{http_code}" https://checkin.taylaibui.vn/ 2>/dev/null || echo "000")"
print_status "HTTPS static: $(curl -s -o /dev/null -w "%{http_code}" https://checkin.taylaibui.vn/static/css/home.css 2>/dev/null || echo "000")"

print_status "✅ Fix completed!"
