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

# 6. Fix permissions FIRST - before any Django operations
print_status "Fixing permissions..."
sudo mkdir -p logs
sudo chown -R www-data:www-data staticfiles/ media/ data/ logs/
sudo chmod -R 755 staticfiles/ media/ data/ logs/
sudo chmod 666 data/*.sqlite3 2>/dev/null || true  # Write permissions for database
sudo touch logs/django.log
sudo chown www-data:www-data logs/django.log
sudo chmod 666 logs/django.log

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
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
    fi
done

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
            WEBSITE_SUCCESS=true
            STATIC_SUCCESS=true
        fi
    fi
fi

# Final verdict - Accept both HTTP 200 and HTTPS redirects as success
WEBSITE_SUCCESS=false
STATIC_SUCCESS=false

if [ "$WEBSITE_STATUS" = "200" ]; then
    WEBSITE_SUCCESS=true
elif [ "$WEBSITE_STATUS" = "301" ] && [ -n "${HTTPS_STATUS:-}" ] && [ "$HTTPS_STATUS" = "200" ]; then
    WEBSITE_SUCCESS=true
    print_status "Website working via HTTPS redirect (normal with SSL)"
fi

if [ "$STATIC_STATUS" = "200" ]; then
    STATIC_SUCCESS=true
elif [ "$STATIC_STATUS" = "301" ] && [ -n "${HTTPS_STATIC_STATUS:-}" ] && [ "$HTTPS_STATIC_STATUS" = "200" ]; then
    STATIC_SUCCESS=true
    print_status "Static files working via HTTPS redirect (normal with SSL)"
fi

if [ "$WEBSITE_SUCCESS" = true ] && [ "$STATIC_SUCCESS" = true ]; then
    print_success "🎉 SUCCESS! Update completed successfully!"
    if [ "$WEBSITE_STATUS" = "200" ]; then
        print_success "✅ Website: $WEBSITE_URL (HTTP 200)"
    else
        print_success "✅ Website: HTTPS version working (redirected from HTTP)"
    fi
    if [ "$STATIC_STATUS" = "200" ]; then
        print_success "✅ Static files: HTTP 200"
    else
        print_success "✅ Static files: HTTPS version working (redirected from HTTP)"
    fi
else
    print_error "❌ Issues detected after update:"
    if [ "$WEBSITE_SUCCESS" != true ]; then
        print_error "Website not accessible on HTTP or HTTPS"
    fi
    if [ "$STATIC_SUCCESS" != true ]; then
        print_error "Static files not accessible on HTTP or HTTPS"
    fi
    
    print_status "Recent service logs:"
    if [ "$ENVIRONMENT" == "test" ]; then
        sudo journalctl -u checkin-taylaibui-test -n 5 --no-pager
    elif [ "$ENVIRONMENT" == "production" ]; then
        sudo journalctl -u reco-qly-production -n 5 --no-pager
    fi
fi

print_status "✅ Safe update script completed!"

# Cleanup old backups (keep last 3)
print_status "Cleaning up old backups..."
ls -t staticfiles.backup.* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null || true