#!/bin/bash
# Quick fix for missing static files after Git pull

set -e

PROJECT_DIR="/var/www/checkin.taylaibui.vn"
ENVIRONMENT=${1:-"test"}

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "🔧 Fixing static files for $ENVIRONMENT environment..."

cd $PROJECT_DIR

# Collect static files
print_status "Collecting static files..."
sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py collectstatic --noinput

# Fix permissions
print_status "Fixing permissions..."
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Copy additional static files if they exist
if [ -d "static" ]; then
    print_status "Copying additional static files..."
    sudo -u www-data cp -r static/* staticfiles/ 2>/dev/null || true
fi

# Restart services
print_status "Restarting services..."
sudo systemctl restart checkin-taylaibui-test nginx

# Wait for services
sleep 3

# Test static files
print_status "Testing static files..."
echo "Testing home.css:"
curl -I http://103.15.51.66/static/css/home.css 2>/dev/null | head -2 || echo "❌ home.css not found"

echo "Testing base.css:"
curl -I http://103.15.51.66/static/css/base.css 2>/dev/null | head -2 || echo "❌ base.css not found"

echo "Testing favicon:"
curl -I http://103.15.51.66/static/favicon.ico 2>/dev/null | head -2 || echo "❌ favicon not found"

print_success "🎉 Static files fix completed!"
print_status "🌐 Test website: http://103.15.51.66"
