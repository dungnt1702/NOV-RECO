#!/bin/bash
# SSL Certificate Setup for checkin.taylaibui.vn

set -e

echo "🔒 Setting up SSL Certificate for checkin.taylaibui.vn"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

print_status "Installing Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

print_status "Obtaining SSL certificate for checkin.taylaibui.vn..."
certbot --nginx -d checkin.taylaibui.vn --non-interactive --agree-tos --email admin@taylaibui.vn

print_status "Setting up automatic renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

print_status "Testing SSL configuration..."
nginx -t
systemctl reload nginx

print_success "🎉 SSL certificate setup completed!"
print_status "🔒 HTTPS URL: https://checkin.taylaibui.vn"
print_status "🔄 Certificate will auto-renew every 90 days"

# Test SSL certificate
print_status "Testing SSL certificate..."
if curl -s https://checkin.taylaibui.vn > /dev/null; then
    print_success "✅ SSL certificate is working correctly!"
else
    print_warning "⚠️ SSL test failed. Please check domain DNS and Nginx config."
fi

echo ""
print_status "📝 SSL Certificate Details:"
certbot certificates

echo ""
print_warning "📋 Next steps:"
print_warning "1. Verify domain DNS points to this server"
print_warning "2. Test HTTPS access: https://checkin.taylaibui.vn"
print_warning "3. Update Django ALLOWED_HOSTS if needed"
print_warning "4. Test certificate auto-renewal: certbot renew --dry-run"
