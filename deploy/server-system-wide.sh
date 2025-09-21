#!/bin/bash

# NOV-RECO Server Manager - System-wide Installation
# Use existing Python environment without virtual environment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="checkin.taylaibui.vn"
DEFAULT_PORT=8000

print_status() { echo -e "${YELLOW}$1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check server status
check_server_status() {
    DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}' | head -1)
    
    if [ -n "$DJANGO_PID" ]; then
        PORT=$(ps aux | grep 'manage.py runserver' | grep -v grep | head -1 | sed 's/.*:\([0-9]*\).*/\1/')
        print_success "Server RUNNING (PID: $DJANGO_PID, Port: $PORT)"
        SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
        echo -e "${GREEN}🌐 External: https://$DOMAIN${NC}"
        echo -e "${GREEN}📡 Direct: http://$SERVER_IP:$PORT${NC}"
        return 0
    else
        print_info "Server NOT running"
        return 1
    fi
}

# Stop server
stop_server() {
    DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}')
    if [ -n "$DJANGO_PID" ]; then
        kill $DJANGO_PID
        print_success "Server stopped"
    fi
}

# Setup system-wide packages
setup_system_packages() {
    print_status "🔧 Installing packages system-wide..."
    
    # Add pip to PATH
    export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"
    
    # Install pip3 if needed
    if ! command -v pip3 &> /dev/null; then
        print_status "📦 Installing pip3..."
        curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
        python3 get-pip.py --user --quiet
        rm -f get-pip.py
        echo 'export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"' >> ~/.bashrc
    fi
    
    # Install packages to user directory
    print_status "📦 Installing Python packages..."
    pip3 install --user --quiet "Django==3.2.25"
    pip3 install --user --quiet "django-allauth==0.53.1"
    pip3 install --user --quiet "djangorestframework==3.14.0"
    pip3 install --user --quiet "Pillow==8.4.0"
    pip3 install --user --quiet "python-dotenv==0.19.2"
    
    # Verify Django installation
    python3 -c "import django; print('✅ Django version:', django.get_version())" || {
        print_error "Django installation failed"
        exit 1
    }
    
    print_success "Packages installed successfully"
}

# Setup Django
setup_django() {
    print_status "🗄️ Setting up Django..."
    
    # Create directories
    mkdir -p data logs media staticfiles
    
    # Set environment variables
    export DJANGO_ENVIRONMENT=test
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1,0.0.0.0"
    
    # Run Django setup
    python3 manage.py migrate --verbosity=0
    python3 manage.py collectstatic --noinput --verbosity=0
    
    # Create admin user
    python3 manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin created: admin/admin123')
else:
    print('ℹ️ Admin already exists')
EOF
    
    print_success "Django setup completed"
}

# Check if packages are installed
check_packages() {
    print_status "🔍 Checking installed packages..."
    
    # Check Django
    if python3 -c "import django" 2>/dev/null; then
        DJANGO_VERSION=$(python3 -c "import django; print(django.get_version())")
        print_success "Django $DJANGO_VERSION installed"
        return 0
    else
        print_info "Django not installed"
        return 1
    fi
}

# Start server
start_server() {
    local port=${1:-$DEFAULT_PORT}
    
    # Check if port is in use
    if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
        print_error "Port $port is in use"
        print_info "Try: $0 auto 8080"
        return 1
    fi
    
    # Set environment variables
    export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"
    export DJANGO_ENVIRONMENT=test
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1,0.0.0.0"
    
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "$(hostname)")
    
    echo ""
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}🎉 NOV-RECO Check-in System Starting...${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}🌐 External URL: https://$DOMAIN${NC}"
    echo -e "${GREEN}🔧 Admin Panel: https://$DOMAIN/admin${NC}"
    echo -e "${BLUE}📡 Direct Access: http://$SERVER_IP:$port${NC}"
    echo -e "${BLUE}🔑 Login: admin/admin123${NC}"
    echo -e "${YELLOW}📊 Press Ctrl+C to stop${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo ""
    
    # Start Django server
    python3 manage.py runserver 0.0.0.0:$port
}

# Main logic
case "${1:-auto}" in
    "status")
        echo -e "${BLUE}📊 NOV-RECO Server Status${NC}"
        echo "=========================="
        check_server_status
        ;;
    "stop")
        echo -e "${BLUE}🛑 Stopping NOV-RECO Server${NC}"
        stop_server
        ;;
    "auto")
        echo -e "${BLUE}🚀 NOV-RECO Auto Setup & Start (System-wide)${NC}"
        echo "=============================================="
        
        # Check if already running
        if check_server_status; then
            echo ""
            read -p "Server running. Restart? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                stop_server
                echo ""
            else
                exit 0
            fi
        fi
        
        # Check and install packages if needed
        if ! check_packages; then
            setup_system_packages
            echo ""
        fi
        
        # Setup Django if needed
        if [ ! -f "data/db_test.sqlite3" ]; then
            setup_django
            echo ""
        fi
        
        # Start server
        start_server ${2:-$DEFAULT_PORT}
        ;;
    "setup")
        echo -e "${BLUE}🔧 NOV-RECO Setup (System-wide)${NC}"
        echo "================================"
        setup_system_packages
        setup_django
        print_success "Setup completed"
        ;;
    *)
        echo -e "${BLUE}🚀 NOV-RECO Server Manager (System-wide)${NC}"
        echo "Usage: $0 [command] [port]"
        echo ""
        echo "Commands:"
        echo "  auto [port]    - Auto setup and start (default: $DEFAULT_PORT)"
        echo "  setup          - Install packages and setup Django"
        echo "  status         - Check server status"
        echo "  stop           - Stop server"
        echo ""
        echo "Examples:"
        echo "  $0 auto        - Setup and start on port $DEFAULT_PORT"
        echo "  $0 auto 8080   - Setup and start on port 8080"
        echo "  $0 setup       - Install packages only"
        echo "  $0 status      - Check if server is running"
        echo "  $0 stop        - Stop running server"
        echo ""
        echo -e "${YELLOW}Note: Uses system-wide Python installation${NC}"
        ;;
esac
