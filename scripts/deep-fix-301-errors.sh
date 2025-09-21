#!/bin/bash
# Deep fix for persistent HTTP 301 redirect errors

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_status "🔧 Deep fixing HTTP 301 redirect issues..."

cd /var/www/checkin.taylaibui.vn

# 1. Check current Nginx config
print_status "Current Nginx config:"
cat /etc/nginx/sites-available/checkin.taylaibui.vn | grep -E "(return|redirect|ssl|443)" || echo "No redirects found"

# 2. Create simple Nginx config without SSL redirects
print_status "Creating simplified Nginx config..."
sudo tee /etc/nginx/sites-available/checkin.taylaibui.vn > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name checkin.taylaibui.vn www.checkin.taylaibui.vn 103.15.51.66;

    # Remove any SSL redirects for now
    # return 301 https://$server_name$request_uri;

    # Serve directly from HTTP for testing
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/checkin.taylaibui.vn/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # Ensure correct MIME types
        location ~* \.(css)$ {
            add_header Content-Type text/css;
        }
        location ~* \.(js)$ {
            add_header Content-Type application/javascript;
        }
        location ~* \.(png|jpg|jpeg|gif|ico|svg)$ {
            add_header Content-Type image/$1;
        }
    }

    # Media files
    location /media/ {
        alias /var/www/checkin.taylaibui.vn/media/;
        expires 30d;
    }
}
NGINXEOF

# 3. Disable HTTPS in Django settings
print_status "Disabling HTTPS in Django settings..."
if [ -f ".env" ]; then
    # Remove or disable SSL settings
    sed -i 's/SECURE_SSL_REDIRECT=1/SECURE_SSL_REDIRECT=0/g' .env
    sed -i 's/SESSION_COOKIE_SECURE=1/SESSION_COOKIE_SECURE=0/g' .env
    sed -i 's/CSRF_COOKIE_SECURE=1/CSRF_COOKIE_SECURE=0/g' .env
    
    # Ensure these are set correctly
    grep -q "SECURE_SSL_REDIRECT=0" .env || echo "SECURE_SSL_REDIRECT=0" >> .env
    grep -q "SESSION_COOKIE_SECURE=0" .env || echo "SESSION_COOKIE_SECURE=0" >> .env
    grep -q "CSRF_COOKIE_SECURE=0" .env || echo "CSRF_COOKIE_SECURE=0" >> .env
    
    print_status "Current security settings:"
    grep -E "(SECURE_SSL_REDIRECT|SESSION_COOKIE_SECURE|CSRF_COOKIE_SECURE)" .env
fi

# 4. Test Nginx config
print_status "Testing Nginx config..."
sudo nginx -t

if [ $? -ne 0 ]; then
    print_error "Nginx config test failed!"
    exit 1
fi

# 5. Restart services in correct order
print_status "Stopping all services..."
sudo systemctl stop checkin-taylaibui-test
sudo systemctl stop nginx

print_status "Starting Django service..."
sudo systemctl start checkin-taylaibui-test
sleep 5

# Check if Django is responding
print_status "Testing Django direct access..."
DJANGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "000")
if [ "$DJANGO_STATUS" != "200" ]; then
    print_error "Django not responding on localhost:8000 (HTTP $DJANGO_STATUS)"
    sudo journalctl -u checkin-taylaibui-test -n 10 --no-pager
    exit 1
else
    print_success "Django responding with HTTP 200"
fi

print_status "Starting Nginx..."
sudo systemctl start nginx
sleep 3

# 6. Test everything
print_status "🧪 Final tests..."

# Test IP access
print_status "Testing IP access..."
IP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://103.15.51.66/)
print_status "IP access: HTTP $IP_STATUS"

# Test domain access
print_status "Testing domain access..."
DOMAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/)
print_status "Domain access: HTTP $DOMAIN_STATUS"

# Test static files
print_status "Testing static files..."
STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://checkin.taylaibui.vn/static/css/home.css)
print_status "Static files: HTTP $STATIC_STATUS"

# 7. Summary
if [ "$DOMAIN_STATUS" = "200" ] && [ "$STATIC_STATUS" = "200" ]; then
    print_success "🎉 SUCCESS! All tests passed"
    print_success "Website: http://checkin.taylaibui.vn/ (HTTP $DOMAIN_STATUS)"
    print_success "Static files: HTTP $STATIC_STATUS"
else
    print_error "❌ Some issues remain:"
    print_error "Website: HTTP $DOMAIN_STATUS (should be 200)"
    print_error "Static files: HTTP $STATIC_STATUS (should be 200)"
    
    print_status "Checking logs..."
    echo "=== Django logs ==="
    sudo journalctl -u checkin-taylaibui-test -n 5 --no-pager
    echo "=== Nginx error log ==="
    sudo tail -5 /var/log/nginx/error.log
fi

print_status "Service status:"
sudo systemctl is-active checkin-taylaibui-test nginx
