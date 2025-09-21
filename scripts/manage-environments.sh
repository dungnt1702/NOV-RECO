#!/bin/bash
# Environment Management Script for NOV-RECO
# Provides easy commands to manage different environments

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

show_help() {
    echo "🔧 NOV-RECO Environment Management"
    echo ""
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  switch [local|test|production]  - Switch environment configuration"
    echo "  deploy [test|production]        - Deploy to server"
    echo "  status [test|production]        - Check server status"
    echo "  logs [test|production]          - View server logs"
    echo "  restart [test|production]       - Restart server services"
    echo "  update [test|production]        - Update server from Git"
    echo ""
    echo "Environments:"
    echo "  🏠 local      - Local development (DEBUG=True, SQLite)"
    echo "  🧪 test       - Test server (DEBUG=True, SQLite, checkin.taylaibui.vn)"
    echo "  🌐 production - Production server (DEBUG=False, PostgreSQL, SSL required)"
    echo ""
    echo "Examples:"
    echo "  $0 switch test                  # Switch to test environment"
    echo "  $0 deploy test                  # Deploy test environment to server"
    echo "  $0 status test                  # Check test server status"
    echo "  $0 update test                  # Update test server from Git"
}

COMMAND=${1:-"help"}
ENVIRONMENT=${2:-"test"}

case $COMMAND in
    switch)
        echo "🔄 Switching to $ENVIRONMENT environment..."
        ./scripts/switch-environment.sh $ENVIRONMENT
        ;;
        
    deploy)
        case $ENVIRONMENT in
            test)
                echo "🧪 Deploying TEST environment to server..."
                echo "📝 Commands to run on server:"
                echo "  cd /var/www/checkin.taylaibui.vn"
                echo "  sudo ./deploy/deploy-test-server.sh"
                ;;
            production)
                echo "🌐 Deploying PRODUCTION environment to server..."
                echo "📝 Commands to run on server:"
                echo "  cd /var/www/checkin.taylaibui.vn"
                echo "  sudo ./deploy/deploy-production-server.sh"
                ;;
            *)
                print_error "Invalid environment for deploy. Use: test or production"
                ;;
        esac
        ;;
        
    status)
        echo "📊 Checking $ENVIRONMENT server status..."
        echo "📝 Commands to run on server:"
        echo "  sudo systemctl status checkin-taylaibui-$ENVIRONMENT"
        echo "  sudo systemctl status nginx"
        ;;
        
    logs)
        echo "📋 Viewing $ENVIRONMENT server logs..."
        echo "📝 Commands to run on server:"
        echo "  sudo journalctl -u checkin-taylaibui-$ENVIRONMENT -f"
        echo "  sudo tail -f /var/log/nginx/error.log"
        ;;
        
    restart)
        echo "🔄 Restarting $ENVIRONMENT server..."
        echo "📝 Commands to run on server:"
        echo "  sudo systemctl restart checkin-taylaibui-$ENVIRONMENT"
        echo "  sudo systemctl restart nginx"
        ;;
        
    update)
        echo "📥 Updating $ENVIRONMENT server from Git..."
        echo "📝 Commands to run on server:"
        echo "  cd /var/www/checkin.taylaibui.vn"
        echo "  sudo ./scripts/update-server-from-git.sh $ENVIRONMENT"
        ;;
        
    help|*)
        show_help
        ;;
esac

echo ""
print_status "🌐 Environment URLs:"
echo "  🏠 Local: http://localhost:3000"
echo "  🧪 Test: http://checkin.taylaibui.vn"
echo "  🌐 Production: https://checkin.taylaibui.vn"
