#!/bin/bash

# NOV-RECO Server Manager - All-in-One Script
# Check environment, setup, start/stop server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="checkin.taylaibui.vn"
DEFAULT_PORT=8000

print_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}🚀 NOV-RECO Server Manager${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

print_status() {
    echo -e "${YELLOW}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Django server is running
check_server_status() {
    print_status "🔍 Checking server status..."
    
    DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}' | head -1)
    
    if [ -n "$DJANGO_PID" ]; then
        PORT=$(ps aux | grep 'manage.py runserver' | grep -v grep | head -1 | sed 's/.*:\([0-9]*\).*/\1/')
        print_success "Server is RUNNING (PID: $DJANGO_PID, Port: $PORT)"
        echo -e "${GREEN}🌐 URL: http://$DOMAIN:$PORT${NC}"
        echo -e "${GREEN}🔧 Admin: http://$DOMAIN:$PORT/admin${NC}"
        return 0
    else
        print_info "Server is NOT running"
        return 1
    fi
}

# Stop server
stop_server() {
    print_status "🛑 Stopping server..."
    
    DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}')
    
    if [ -n "$DJANGO_PID" ]; then
        kill $DJANGO_PID
        print_success "Server stopped (PID: $DJANGO_PID)"
    else
        print_info "No server process found"
    fi
}

# Check environment
check_environment() {
    print_status "🔍 Checking environment..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python: $PYTHON_VERSION"
    else
        print_error "Python3 not found"
        exit 1
    fi
    
    # Check project
    if [ -f "manage.py" ]; then
        print_success "Django project detected"
    else
        print_error "Django project not found (manage.py missing)"
        exit 1
    fi
    
    # Check virtual environment
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        print_success "Virtual environment exists"
        return 0
    else
        print_info "Virtual environment needs setup"
        return 1
    fi
}

# Setup environment
setup_environment() {
    print_status "🔧 Setting up environment..."
    
    # Add pip to PATH
    export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"
    
    # Install pip3 if needed
    if ! command -v pip3 &> /dev/null; then
        print_status "📦 Installing pip3..."
        curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
        python3 get-pip.py --user --quiet
        rm -f get-pip.py
    fi
    
    # Create virtual environment
    print_status "🐍 Creating virtual environment..."
    rm -rf venv
    python3 -m venv --without-pip venv
    source venv/bin/activate
    
    # Install pip in venv
    curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
    python get-pip.py --quiet
    rm -f get-pip.py
    
    # Install packages
    print_status "📦 Installing packages..."
    pip install --quiet "Django==3.2.25" "django-allauth==0.54.0" "djangorestframework==3.14.0" "Pillow==8.4.0" "python-dotenv==0.19.2"
    
    # Setup Django
    print_status "🗄️ Setting up Django..."
    mkdir -p data logs media staticfiles
    
    export DJANGO_ENVIRONMENT=test
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1,0.0.0.0"
    
    python manage.py migrate --verbosity=0
    python manage.py collectstatic --noinput --verbosity=0
    
    # Create admin user
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin created: admin/admin123')
EOF
    
    print_success "Environment setup completed"
}

# Start server
start_server() {
    local port=${1:-$DEFAULT_PORT}
    
    print_status "🚀 Starting server on port $port..."
    
    # Check if port is in use
    if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
        print_error "Port $port is already in use"
        print_info "Try a different port: ./server-manager.sh start 8080"
        return 1
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Set environment variables
    export DJANGO_ENVIRONMENT=test
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1,0.0.0.0"
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    
    echo ""
    print_success "🎉 NOV-RECO Check-in System Starting..."
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}🌐 External URL: https://$DOMAIN${NC}"
    echo -e "${GREEN}🔧 Admin Panel: https://$DOMAIN/admin${NC}"
    echo -e "${BLUE}📡 Direct Access: http://$SERVER_IP:$port${NC}"
    echo -e "${BLUE}🔑 Login: admin/admin123${NC}"
    echo -e "${YELLOW}📊 Press Ctrl+C to stop server${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo ""
    
    # Start Django server
    python manage.py runserver 0.0.0.0:$port
}

# Show usage
show_usage() {
    echo "Usage: $0 [command] [port]"
    echo ""
    echo "Commands:"
    echo "  status           - Check server status"
    echo "  setup            - Setup environment"
    echo "  start [port]     - Start server (default port: $DEFAULT_PORT)"
    echo "  stop             - Stop server"
    echo "  restart [port]   - Restart server"
    echo "  auto [port]      - Auto setup and start (recommended)"
    echo ""
    echo "Examples:"
    echo "  $0 auto          - Setup and start on port $DEFAULT_PORT"
    echo "  $0 auto 8080     - Setup and start on port 8080"
    echo "  $0 start         - Start server on port $DEFAULT_PORT"
    echo "  $0 start 8080    - Start server on port 8080"
    echo "  $0 status        - Check if server is running"
    echo "  $0 stop          - Stop running server"
}

# Auto setup and start
auto_setup() {
    local port=${1:-$DEFAULT_PORT}
    
    print_header
    
    # Check current status
    if check_server_status; then
        echo ""
        read -p "Server is already running. Stop and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_server
            echo ""
        else
            print_info "Keeping current server running"
            return 0
        fi
    fi
    
    # Check environment
    if ! check_environment; then
        echo ""
        print_status "🔧 Environment needs setup..."
        setup_environment
        echo ""
    fi
    
    # Start server
    start_server $port
}

# Main script logic
case "${1:-auto}" in
    "status")
        print_header
        check_server_status
        echo ""
        ;;
    "setup")
        print_header
        check_environment || setup_environment
        print_success "Setup completed"
        echo ""
        ;;
    "start")
        print_header
        if ! check_environment; then
            print_error "Environment not setup. Run: $0 setup"
            exit 1
        fi
        start_server ${2:-$DEFAULT_PORT}
        ;;
    "stop")
        print_header
        stop_server
        echo ""
        ;;
    "restart")
        print_header
        stop_server
        echo ""
        if ! check_environment; then
            print_error "Environment not setup. Run: $0 setup"
            exit 1
        fi
        start_server ${2:-$DEFAULT_PORT}
        ;;
    "auto")
        auto_setup ${2:-$DEFAULT_PORT}
        ;;
    "help"|"-h"|"--help")
        print_header
        show_usage
        ;;
    *)
        print_header
        show_usage
        ;;
esac
