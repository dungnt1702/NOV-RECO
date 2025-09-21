#!/bin/bash

# NOV-RECO Server Manager - Python 3.6 Compatible
# Fixed package versions for Python 3.6

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

# Setup environment with Python 3.6 compatible packages
setup_environment() {
    print_status "🔧 Setting up environment for Python 3.6..."
    
    # Add pip to PATH
    export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"
    
    # Install pip3 if needed
    if ! command -v pip3 &> /dev/null; then
        print_status "📦 Installing pip3..."
        curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
        python3 get-pip.py --user --quiet
        rm -f get-pip.py
    fi
    
    # Create venv
    print_status "🐍 Creating virtual environment..."
    rm -rf venv
    python3 -m venv --without-pip venv
    source venv/bin/activate
    
    # Install pip in venv
    curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
    python get-pip.py --quiet
    rm -f get-pip.py
    
    # Install Python 3.6 compatible packages
    print_status "📦 Installing Python 3.6 compatible packages..."
    
    # Install packages one by one with compatible versions
    pip install --quiet "Django==3.2.25"
    pip install --quiet "django-allauth==0.53.1"  # Last version for Python 3.6
    pip install --quiet "djangorestframework==3.14.0"
    pip install --quiet "Pillow==8.4.0"
    pip install --quiet "python-dotenv==0.19.2"
    
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
    print('✅ Admin created: admin/admin123')
else:
    print('ℹ️ Admin already exists')
EOF
    
    print_success "Environment setup completed"
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
    
    # Activate venv and start
    source venv/bin/activate
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
    
    python manage.py runserver 0.0.0.0:$port
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
        echo -e "${BLUE}🚀 NOV-RECO Auto Setup & Start${NC}"
        echo "==============================="
        
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
        
        # Setup if needed
        if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
            setup_environment
            echo ""
        fi
        
        # Start server
        start_server ${2:-$DEFAULT_PORT}
        ;;
    *)
        echo -e "${BLUE}🚀 NOV-RECO Server Manager${NC}"
        echo "Usage: $0 [command] [port]"
        echo ""
        echo "Commands:"
        echo "  auto [port]    - Auto setup and start (default: $DEFAULT_PORT)"
        echo "  status         - Check server status"
        echo "  stop           - Stop server"
        echo ""
        echo "Examples:"
        echo "  $0 auto        - Setup and start on port $DEFAULT_PORT"
        echo "  $0 auto 8080   - Setup and start on port 8080"
        echo "  $0 status      - Check if server is running"
        echo "  $0 stop        - Stop running server"
        ;;
esac
