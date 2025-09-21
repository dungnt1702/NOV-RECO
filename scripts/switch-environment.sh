#!/bin/bash
# Environment Switcher Script for NOV-RECO
# Usage: ./scripts/switch-environment.sh [local|test|production]

set -e

ENVIRONMENT=${1:-"local"}
PROJECT_DIR=$(pwd)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔄 Switching to $ENVIRONMENT environment..."

# Validate environment
case $ENVIRONMENT in
    local|test|production)
        ;;
    *)
        print_error "Invalid environment. Use: local, test, or production"
        exit 1
        ;;
esac

# Check if config file exists
CONFIG_FILE="config/${ENVIRONMENT}.env"
if [ ! -f "$CONFIG_FILE" ]; then
    print_error "Configuration file $CONFIG_FILE not found!"
    exit 1
fi

print_status "Copying $ENVIRONMENT configuration..."
cp "$CONFIG_FILE" .env

print_status "Environment variables for $ENVIRONMENT:"
echo "----------------------------------------"
cat .env | grep -E "^(DJANGO_|DATABASE_|ALLOWED_|DEBUG|SERVER_)" | head -10
echo "----------------------------------------"

# Environment-specific setup
case $ENVIRONMENT in
    local)
        print_status "Setting up LOCAL development environment..."
        echo "🏠 Local Development Setup:"
        echo "  - DEBUG=True"
        echo "  - SQLite database: data/db.sqlite3"
        echo "  - Console email backend"
        echo "  - Relaxed security settings"
        echo ""
        echo "📝 To start local server:"
        echo "  ./scripts/run-local.sh"
        echo "  or"
        echo "  python manage.py runserver 3000"
        ;;
        
    test)
        print_status "Setting up TEST environment..."
        echo "🧪 Test Environment Setup:"
        echo "  - DEBUG=True (for detailed errors)"
        echo "  - SQLite database: data/db_test.sqlite3"
        echo "  - Console email backend"
        echo "  - Relaxed security for testing"
        echo ""
        echo "📝 To deploy on test server:"
        echo "  sudo ./deploy/deploy-test-server.sh"
        ;;
        
    production)
        print_status "Setting up PRODUCTION environment..."
        echo "🌐 Production Environment Setup:"
        echo "  - DEBUG=False"
        echo "  - PostgreSQL database (recommended)"
        echo "  - SMTP email backend"
        echo "  - Strict security settings"
        echo "  - SSL required"
        echo ""
        print_warning "⚠️  PRODUCTION checklist:"
        print_warning "  1. Change DJANGO_SECRET_KEY"
        print_warning "  2. Update database credentials"
        print_warning "  3. Configure email settings"
        print_warning "  4. Setup SSL certificates"
        print_warning "  5. Update ALLOWED_HOSTS"
        echo ""
        echo "📝 To deploy on production server:"
        echo "  sudo ./deploy/deploy-production-server.sh"
        ;;
esac

print_success "✅ Switched to $ENVIRONMENT environment!"
print_status "📁 Configuration file: .env"
print_status "🔧 Current settings loaded from: $CONFIG_FILE"

# Show next steps
echo ""
print_status "🚀 Next steps:"
case $ENVIRONMENT in
    local)
        echo "  1. Install dependencies: pip install -r requirements.txt"
        echo "  2. Run migrations: python manage.py migrate"
        echo "  3. Start server: ./scripts/run-local.sh"
        ;;
    test)
        echo "  1. Upload to server: scp -r . user@server:/var/www/checkin.taylaibui.vn"
        echo "  2. SSH to server: ssh user@server"
        echo "  3. Run deployment: sudo ./deploy/deploy-test-server.sh"
        ;;
    production)
        echo "  1. Review and update .env file with production values"
        echo "  2. Upload to server: scp -r . user@server:/var/www/production"
        echo "  3. SSH to server: ssh user@server"
        echo "  4. Run deployment: sudo ./deploy/deploy-production-server.sh"
        ;;
esac
