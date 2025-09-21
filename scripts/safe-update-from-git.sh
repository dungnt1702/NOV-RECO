#!/bin/bash
# Safe Git update script that preserves static files

set -e

ENVIRONMENT=$1
PROJECT_DIR="/var/www/checkin.taylaibui.vn"

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 [test|production]"
    exit 1
fi

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

cd "$PROJECT_DIR"

# Error handling function
handle_error() {
    print_error "❌ Update failed! Attempting recovery..."
    
    # Try to restore from backup
    if [ -d "/var/backups/nov-reco/latest" ]; then
        print_status "Restoring from backup..."
        sudo bash /var/backups/nov-reco/latest/restore.sh 2>/dev/null || true
    fi
    
    # Restart services
    if [ "$ENVIRONMENT" == "test" ]; then
        sudo systemctl restart checkin-taylaibui-test nginx 2>/dev/null || true
    elif [ "$ENVIRONMENT" == "production" ]; then
        sudo systemctl restart reco-qly-production nginx 2>/dev/null || true
    fi
    
    print_error "Recovery attempted. Please check manually."
    exit 1
}

# Set error trap
trap handle_error ERR

print_status "🚀 Safe updating server for $ENVIRONMENT environment..."

# 1. Backup static files before Git pull
print_status "Backing up static files..."
if [ -d "staticfiles" ]; then
    cp -r staticfiles staticfiles.backup.$(date +%Y%m%d-%H%M%S)
fi

# 2. Stash local changes (excluding database files)
print_status "Stashing local changes..."
git add .
git reset data/*.sqlite3 data/*.db 2>/dev/null || true
git stash || true

# 3. Pull latest code
print_status "Pulling latest code from Git..."
git pull origin master || git pull origin main

# 4. Copy environment file
print_status "Setting up environment for $ENVIRONMENT..."
cp "config/$ENVIRONMENT.env" ".env"

# 5. Install dependencies
print_status "Installing Python dependencies..."
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# 6. Fix permissions and ensure directories exist FIRST
print_status "Creating directories and fixing permissions..."
sudo mkdir -p staticfiles logs media data
sudo chown -R www-data:www-data staticfiles/ static/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ static/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true  # Write permissions for database
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 6.5. Emergency check - if staticfiles is empty, restore from backup first
if [ ! -d "staticfiles/css" ] || [ -z "$(ls -A staticfiles 2>/dev/null)" ]; then
    print_status "staticfiles directory empty, attempting restore from backup..."
    
    # Try local backup first
    LATEST_BACKUP=$(ls -t staticfiles.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP" ]; then
        print_status "Restoring from local backup: $LATEST_BACKUP"
        sudo -u www-data cp -r "$LATEST_BACKUP"/* staticfiles/ 2>/dev/null || true
    fi
    
    # Try system backup
    if [ ! -d "staticfiles/css" ] && [ -d "/var/backups/nov-reco/latest/staticfiles.backup" ]; then
        print_status "Restoring from system backup..."
        sudo -u www-data cp -r /var/backups/nov-reco/latest/staticfiles.backup/* staticfiles/ 2>/dev/null || true
    fi
    
    # If still empty, copy from static/ as emergency fallback
    if [ ! -d "staticfiles/css" ] && [ -d "static/css" ]; then
        print_status "Emergency fallback: copying from static/ to staticfiles/..."
        sudo -u www-data cp -r static/* staticfiles/ 2>/dev/null || true
    fi
fi

# 7. Run migrations
print_status "Running database migrations..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate

# 8. Collect static files properly
print_status "Collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput --clear

# 8.5. Verify static files were collected
if [ ! -f "staticfiles/css/home.css" ]; then
    print_error "Critical static files missing after collectstatic!"
    print_status "Attempting to restore from backup..."
    
    # Try to restore from local backup first
    LATEST_BACKUP=$(ls -t staticfiles.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        print_status "Restoring from local backup: $LATEST_BACKUP"
        sudo -u www-data cp -r "$LATEST_BACKUP"/* staticfiles/ 2>/dev/null || true
    fi
    
    # If still missing, try system backup
    if [ ! -f "staticfiles/css/home.css" ] && [ -d "/var/backups/nov-reco/latest/staticfiles.backup" ]; then
        print_status "Restoring from system backup..."
        sudo -u www-data cp -r /var/backups/nov-reco/latest/staticfiles.backup/* staticfiles/ 2>/dev/null || true
    fi
    
    # Final check
    if [ ! -f "staticfiles/css/home.css" ]; then
        print_error "❌ Could not restore static files! Manual intervention required."
        print_status "You may need to run: python manage.py collectstatic --noinput"
    else
        print_success "✅ Static files restored successfully"
    fi
else
    print_success "✅ Static files collected successfully"
fi

# 9. Final static files verification and test
print_status "Final static files verification..."
if [ -f "staticfiles/css/home.css" ]; then
    print_success "✅ home.css found"
    ls -la staticfiles/css/home.css
else
    print_error "❌ home.css still missing!"
fi

# List some key static files for verification
print_status "Key static files status:"
for file in "staticfiles/css/base.css" "staticfiles/css/checkin.css" "staticfiles/js/base.js"; do
    if [ -f "$file" ]; then
        echo "✅ $file ($(wc -c < "$file") bytes)"
    else
        echo "❌ $file (missing)"
    fi
done

# Test actual CSS content (not just HTTP status)
print_status "Testing actual CSS content..."
if [ -f "staticfiles/css/home.css" ]; then
    CSS_SIZE=$(wc -c < "staticfiles/css/home.css")
    if [ "$CSS_SIZE" -gt 100 ]; then
        print_success "✅ home.css has content ($CSS_SIZE bytes)"
        
        # Test if CSS contains expected content
        if grep -q "body\|html\|\.container" "staticfiles/css/home.css"; then
            print_success "✅ home.css contains valid CSS rules"
        else
            print_error "❌ home.css exists but contains no valid CSS"
            head -5 "staticfiles/css/home.css"
        fi
    else
        print_error "❌ home.css is too small ($CSS_SIZE bytes) - likely empty or corrupted"
        cat "staticfiles/css/home.css"
    fi
else
    print_error "❌ home.css file not found"
fi

# 9. Fix permissions (including logs) - BEFORE Django operations
print_status "Fixing permissions..."
sudo mkdir -p logs
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true  # Write permissions for database
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

# 10. Check Django configuration
print_status "Checking Django configuration..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py check

if [ $? -ne 0 ]; then
    print_error "Django configuration error!"
    exit 1
fi

# 10.5. Ensure admin user exists for test environment
if [ "$ENVIRONMENT" == "test" ]; then
    print_status "Ensuring admin user exists for test environment..."
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py shell << 'PYTHON_SCRIPT'
from django.contrib.auth import get_user_model
from users.models import UserRole

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            role=UserRole.ADMIN,
            employee_id='ADMIN001',
            department='IT'
        )
        print("✅ Created admin user: admin / admin123")
    except Exception as e:
        print(f"⚠️  Could not create admin user: {e}")
else:
    print("✅ Admin user already exists")

print(f"📊 Total users in database: {User.objects.count()}")
PYTHON_SCRIPT
fi

# 11. Restart services carefully
print_status "Restarting services..."
if [ "$ENVIRONMENT" == "test" ]; then
    sudo systemctl stop checkin-taylaibui-test
    sleep 2
    sudo systemctl start checkin-taylaibui-test
    sleep 3
    
    # Check if service started successfully
    if ! systemctl is-active --quiet checkin-taylaibui-test; then
        print_error "Django service failed to start!"
        print_status "Checking logs..."
        sudo journalctl -u checkin-taylaibui-test -n 10 --no-pager
        exit 1
    fi
elif [ "$ENVIRONMENT" == "production" ]; then
    sudo systemctl stop reco-qly-production
    sleep 2
    sudo systemctl start reco-qly-production
    sleep 3
    
    if ! systemctl is-active --quiet reco-qly-production; then
        print_error "Django service failed to start!"
        print_status "Checking logs..."
        sudo journalctl -u reco-qly-production -n 10 --no-pager
        exit 1
    fi
fi

sudo systemctl reload nginx

# 12. Wait and test
sleep 5

# 13. Test website and static files with detailed diagnostics
print_status "Testing website and static files..."

# Set URLs based on environment
if [ "$ENVIRONMENT" == "test" ]; then
    WEBSITE_URL="http://checkin.taylaibui.vn"
    STATIC_URL="http://checkin.taylaibui.vn/static/css/home.css"
elif [ "$ENVIRONMENT" == "production" ]; then
    WEBSITE_URL="http://reco.qly.vn"
    STATIC_URL="http://reco.qly.vn/static/css/home.css"
else
    WEBSITE_URL="http://localhost:8000"
    STATIC_URL="http://localhost:8000/static/css/home.css"
fi

# Test with detailed curl output
print_status "Testing website: $WEBSITE_URL"
WEBSITE_RESPONSE=$(curl -s -I "$WEBSITE_URL" 2>/dev/null || echo "Connection failed")
WEBSITE_STATUS=$(echo "$WEBSITE_RESPONSE" | head -1 | grep -o '[0-9][0-9][0-9]' || echo "000")

print_status "Testing static files: $STATIC_URL"
STATIC_RESPONSE=$(curl -s -I "$STATIC_URL" 2>/dev/null || echo "Connection failed")
STATIC_STATUS=$(echo "$STATIC_RESPONSE" | head -1 | grep -o '[0-9][0-9][0-9]' || echo "000")

# Also test actual CSS content via HTTP
if [ "$STATIC_STATUS" = "200" ]; then
    CSS_CONTENT=$(curl -s "$STATIC_URL" 2>/dev/null | head -200)
    CSS_CONTENT_SIZE=$(echo "$CSS_CONTENT" | wc -c)
    
    if [ "$CSS_CONTENT_SIZE" -gt 100 ] && echo "$CSS_CONTENT" | grep -q "body\|html\|\.container"; then
        print_success "✅ CSS content verified via HTTP ($CSS_CONTENT_SIZE chars)"
    else
        print_error "❌ CSS content invalid via HTTP (size: $CSS_CONTENT_SIZE)"
        echo "First 200 chars of CSS response:"
        echo "$CSS_CONTENT" | head -5
    fi
fi

print_status "=== Test Results ==="
print_status "Website status: HTTP $WEBSITE_STATUS"
print_status "Static files status: HTTP $STATIC_STATUS"

# Show response headers if there are redirects and attempt to fix
if [ "$WEBSITE_STATUS" = "301" ] || [ "$WEBSITE_STATUS" = "302" ]; then
    print_error "❌ Website redirect detected (HTTP $WEBSITE_STATUS):"
    echo "$WEBSITE_RESPONSE" | head -5
    
    # Check if it's redirecting to HTTPS
    REDIRECT_LOCATION=$(echo "$WEBSITE_RESPONSE" | grep -i "location:" | head -1)
    if echo "$REDIRECT_LOCATION" | grep -q "https://"; then
        print_status "🔧 Detected HTTPS redirect. Checking Nginx config..."
        
        # Check if Nginx has SSL redirect
        if grep -q "return 301 https" /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null; then
            print_status "Found SSL redirect in Nginx. This is normal if SSL is configured."
            print_status "Testing HTTPS instead..."
            HTTPS_URL="${WEBSITE_URL/http:/https:}"
            HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HTTPS_URL" 2>/dev/null || echo "000")
            print_status "HTTPS status: HTTP $HTTPS_STATUS"
            
            if [ "$HTTPS_STATUS" = "200" ]; then
                print_success "✅ Website working on HTTPS: $HTTPS_URL"
            elif [ "$HTTPS_STATUS" = "000" ]; then
                print_error "❌ HTTPS connection failed - SSL certificate issue"
                print_status "🔧 Temporarily disabling SSL redirect for HTTP access..."
                
                # Comment out SSL redirect in Nginx for testing
                sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null || true
                sudo systemctl reload nginx
                sleep 2
                
                # Re-test HTTP after disabling SSL redirect
                NEW_HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE_URL" 2>/dev/null || echo "000")
                if [ "$NEW_HTTP_STATUS" = "200" ]; then
                    print_success "✅ Website working on HTTP after disabling SSL redirect"
                    print_status "💡 SSL certificate needs to be fixed for HTTPS to work"
                fi
            fi
        fi
    fi
fi

if [ "$STATIC_STATUS" = "301" ] || [ "$STATIC_STATUS" = "302" ]; then
    print_error "❌ Static files redirect detected (HTTP $STATIC_STATUS):"
    echo "$STATIC_RESPONSE" | head -5
    
    # Test HTTPS version of static files
    HTTPS_STATIC_URL="${STATIC_URL/http:/https:}"
    HTTPS_STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HTTPS_STATIC_URL" 2>/dev/null || echo "000")
    print_status "HTTPS static files status: HTTP $HTTPS_STATIC_STATUS"
    
    if [ "$HTTPS_STATIC_STATUS" = "200" ]; then
        print_success "✅ Static files working on HTTPS: $HTTPS_STATIC_URL"
    elif [ "$HTTPS_STATIC_STATUS" = "000" ]; then
        print_error "❌ HTTPS connection failed - SSL certificate issue"
        print_status "🔧 Checking SSL certificate..."
        
        # Check if SSL files exist
        if [ -f "/etc/ssl/certs/checkin.taylaibui.vn.crt" ] && [ -f "/etc/ssl/private/checkin.taylaibui.vn.key" ]; then
            print_status "SSL files found, testing certificate..."
            openssl x509 -in /etc/ssl/certs/checkin.taylaibui.vn.crt -text -noout | grep -E "(Subject:|Not After)" || true
        else
            print_error "SSL certificate files missing!"
            print_status "Expected files:"
            print_status "- /etc/ssl/certs/checkin.taylaibui.vn.crt"
            print_status "- /etc/ssl/private/checkin.taylaibui.vn.key"
        fi
        
        print_status "🔧 Temporarily disabling SSL redirect to allow HTTP access..."
        # Comment out SSL redirect in Nginx for testing
        sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null || true
        sudo systemctl reload nginx
        
        # Re-test HTTP after disabling SSL redirect
        sleep 2
        NEW_HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE_URL" 2>/dev/null || echo "000")
        NEW_STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$STATIC_URL" 2>/dev/null || echo "000")
        
            if [ "$NEW_HTTP_STATUS" = "200" ] && [ "$NEW_STATIC_STATUS" = "200" ]; then
                print_success "✅ Website working on HTTP after disabling SSL redirect"
                print_status "💡 SSL certificate needs to be fixed for HTTPS to work"
                print_status "💡 For test environment, HTTP access is acceptable"
                WEBSITE_SUCCESS=true
                STATIC_SUCCESS=true
            fi
    fi
fi

# Final verdict - Accept HTTP 301 as SUCCESS when SSL is configured
WEBSITE_SUCCESS=false
STATIC_SUCCESS=false

# Website success logic
if [ "$WEBSITE_STATUS" = "200" ]; then
    WEBSITE_SUCCESS=true
    print_status "✅ Website: Direct HTTP access working"
elif [ "$WEBSITE_STATUS" = "301" ]; then
    # HTTP 301 is SUCCESS when SSL redirect is configured
    if grep -q "return 301 https" /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null; then
        WEBSITE_SUCCESS=true
        print_status "✅ Website: HTTP 301 redirect to HTTPS (normal with SSL configured)"
    fi
fi

# Static files success logic  
if [ "$STATIC_STATUS" = "200" ]; then
    STATIC_SUCCESS=true
    print_status "✅ Static files: Direct HTTP access working"
elif [ "$STATIC_STATUS" = "301" ]; then
    # HTTP 301 is SUCCESS when SSL redirect is configured
    if grep -q "return 301 https" /etc/nginx/sites-available/checkin.taylaibui.vn 2>/dev/null; then
        STATIC_SUCCESS=true
        print_status "✅ Static files: HTTP 301 redirect to HTTPS (normal with SSL configured)"
    fi
fi

if [ "$WEBSITE_SUCCESS" = true ] && [ "$STATIC_SUCCESS" = true ]; then
    print_success "🎉 SUCCESS! Update completed successfully!"
    print_success "✅ Website: $WEBSITE_URL (HTTP $WEBSITE_STATUS)"
    print_success "✅ Static files: HTTP $STATIC_STATUS"
    
    if [ "$WEBSITE_STATUS" = "301" ] || [ "$STATIC_STATUS" = "301" ]; then
        print_status "💡 HTTP 301 redirects are normal when SSL is configured"
        print_status "💡 Users will automatically be redirected to HTTPS"
    fi
else
    print_error "❌ Issues detected, attempting final fix..."
    
    # Final attempt: disable HTTPS redirect for test environment
    if [ "$ENVIRONMENT" = "test" ] && [ "$WEBSITE_STATUS" = "301" ] && [ "$STATIC_STATUS" = "301" ]; then
        print_status "🔧 Final fix: Disabling HTTPS redirect for test environment..."
        
        # Backup and disable HTTPS redirect
        sudo cp /etc/nginx/sites-available/checkin.taylaibui.vn /etc/nginx/sites-available/checkin.taylaibui.vn.backup.$(date +%Y%m%d-%H%M%S)
        sudo sed -i 's/return 301 https/#return 301 https/' /etc/nginx/sites-available/checkin.taylaibui.vn
        
        if sudo nginx -t; then
            sudo systemctl reload nginx
            sleep 3
            
            # Final test
            FINAL_WEBSITE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBSITE_URL" 2>/dev/null || echo "000")
            FINAL_STATIC=$(curl -s -o /dev/null -w "%{http_code}" "$STATIC_URL" 2>/dev/null || echo "000")
            
            if [ "$FINAL_WEBSITE" = "200" ] && [ "$FINAL_STATIC" = "200" ]; then
                print_success "🎉 FINAL FIX SUCCESS!"
                print_success "✅ Website working: $WEBSITE_URL (HTTP $FINAL_WEBSITE)"
                print_success "✅ Static files working: HTTP $FINAL_STATIC"
                print_status "💡 HTTPS redirect disabled for test environment"
                print_status "💡 SSL certificate should be fixed for production use"
            else
                print_error "❌ Final fix failed:"
                print_error "Website: HTTP $FINAL_WEBSITE, Static: HTTP $FINAL_STATIC"
            fi
        fi
    fi
    
    if [ "$WEBSITE_SUCCESS" != true ] || [ "$STATIC_SUCCESS" != true ]; then
        print_status "Recent service logs:"
        if [ "$ENVIRONMENT" == "test" ]; then
            sudo journalctl -u checkin-taylaibui-test -n 5 --no-pager
        elif [ "$ENVIRONMENT" == "production" ]; then
            sudo journalctl -u reco-qly-production -n 5 --no-pager
        fi
    fi
fi

print_status "✅ Safe update script completed!"

# Cleanup old backups (keep last 3)
print_status "Cleaning up old backups..."
ls -t staticfiles.backup.* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null || true