#!/bin/bash

# NOV-RECO Check-in System Setup Script for Python 3.6
# Compatible with shared hosting environment
# Author: NOV-RECO Development Team
# Version: 1.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

print_step() {
    echo -e "${YELLOW}📦 Step $1: $2${NC}"
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

# Main setup function
main() {
    print_header "NOV-RECO Check-in System Setup (Python 3.6)"
    
    # Step 1: Check Python version
    print_step "1" "Checking Python version..."
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "Found: $PYTHON_VERSION"
    
    if [[ $PYTHON_VERSION == *"3.6"* ]]; then
        print_success "Python 3.6 detected - compatible!"
    else
        print_error "Python 3.6 required but found: $PYTHON_VERSION"
        exit 1
    fi
    
    # Step 2: Install pip3 for Python 3.6
    print_step "2" "Installing pip3 for Python 3.6..."
    
    # Remove old get-pip.py if exists
    rm -f get-pip.py
    
    # Download get-pip.py for Python 3.6
    curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
    
    if [ $? -eq 0 ]; then
        print_success "Downloaded get-pip.py"
    else
        print_error "Failed to download get-pip.py"
        exit 1
    fi
    
    # Install pip3
    python3 get-pip.py --user --quiet
    
    # Add pip to PATH
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    
    print_success "pip3 installed successfully"
    
    # Step 3: Create virtual environment
    print_step "3" "Creating virtual environment..."
    
    # Remove existing venv
    rm -rf venv
    
    # Create new venv
    python3 -m venv venv
    
    if [ -d "venv" ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Create python symlink for compatibility
    ln -sf python3 venv/bin/python
    
    # Step 4: Upgrade pip in virtual environment
    print_step "4" "Upgrading pip in virtual environment..."
    
    # Upgrade pip (compatible with Python 3.6)
    python -m pip install --upgrade "pip<21.0" --quiet
    
    print_success "pip upgraded successfully"
    
    # Step 5: Create requirements file for Python 3.6
    print_step "5" "Creating Python 3.6 compatible requirements..."
    
    cat > requirements-py36.txt << 'EOF'
Django==3.2.25
django-allauth==0.54.0
djangorestframework==3.14.0
Pillow==8.4.0
python-dotenv==0.19.2
EOF
    
    print_success "Requirements file created"
    
    # Step 6: Install Python packages
    print_step "6" "Installing Python packages..."
    
    pip install -r requirements-py36.txt --quiet
    
    if [ $? -eq 0 ]; then
        print_success "All packages installed successfully"
    else
        print_error "Failed to install packages"
        exit 1
    fi
    
    # Step 7: Create necessary directories
    print_step "7" "Creating project directories..."
    
    mkdir -p data logs media staticfiles
    
    print_success "Directories created"
    
    # Step 8: Set environment variables
    print_step "8" "Setting environment variables..."
    
    export DJANGO_ENVIRONMENT=test
    export DJANGO_SECRET_KEY="test-secret-key-$(date +%s)"
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0"
    
    print_success "Environment variables set"
    
    # Step 9: Django database setup
    print_step "9" "Setting up Django database..."
    
    python manage.py migrate --verbosity=0
    
    if [ $? -eq 0 ]; then
        print_success "Database migrations completed"
    else
        print_error "Database migration failed"
        exit 1
    fi
    
    # Step 10: Collect static files
    print_step "10" "Collecting static files..."
    
    python manage.py collectstatic --noinput --verbosity=0
    
    if [ $? -eq 0 ]; then
        print_success "Static files collected"
    else
        print_error "Failed to collect static files"
        exit 1
    fi
    
    # Step 11: Create admin user
    print_step "11" "Creating admin user..."
    
    python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️ Admin user already exists')
PYEOF
    
    # Step 12: Create startup script
    print_step "12" "Creating startup script..."
    
    cat > start_server.sh << 'STARTEOF'
#!/bin/bash

# NOV-RECO Check-in System Startup Script
# Usage: ./start_server.sh [port]

# Default port
PORT=${1:-8000}

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting NOV-RECO Check-in System...${NC}"
echo -e "${BLUE}=================================================${NC}"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

# Set environment variables
export DJANGO_ENVIRONMENT=test
export DJANGO_SECRET_KEY="test-secret-key-$(date +%s)"
export DATABASE_NAME=data/db_test.sqlite3
export ALLOWED_HOSTS="checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0"

# Display information
echo -e "${YELLOW}📍 Environment: $DJANGO_ENVIRONMENT${NC}"
echo -e "${YELLOW}🗄️ Database: $DATABASE_NAME${NC}"
echo -e "${YELLOW}🌐 Port: $PORT${NC}"
echo ""
echo -e "${BLUE}🌐 URLs:${NC}"
echo -e "${GREEN}   Website: http://checkin.taylaibui.vn:$PORT${NC}"
echo -e "${GREEN}   Admin:   http://checkin.taylaibui.vn:$PORT/admin${NC}"
echo ""
echo -e "${BLUE}🔑 Login credentials:${NC}"
echo -e "${GREEN}   Username: admin${NC}"
echo -e "${GREEN}   Password: admin123${NC}"
echo ""
echo -e "${BLUE}📊 Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Start Django development server
python manage.py runserver 0.0.0.0:$PORT
STARTEOF
    
    chmod +x start_server.sh
    
    print_success "Startup script created"
    
    # Step 13: Create stop script
    print_step "13" "Creating stop script..."
    
    cat > stop_server.sh << 'STOPEOF'
#!/bin/bash

# NOV-RECO Check-in System Stop Script

echo "🛑 Stopping NOV-RECO Check-in System..."

# Find and kill Django processes
DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}')

if [ -n "$DJANGO_PID" ]; then
    kill $DJANGO_PID
    echo "✅ Django server stopped (PID: $DJANGO_PID)"
else
    echo "ℹ️ No Django server process found"
fi

echo "✅ Stop script completed"
STOPEOF
    
    chmod +x stop_server.sh
    
    print_success "Stop script created"
    
    # Step 14: Create status script
    print_step "14" "Creating status script..."
    
    cat > status_server.sh << 'STATUSEOF'
#!/bin/bash

# NOV-RECO Check-in System Status Script

echo "📊 NOV-RECO Check-in System Status"
echo "=================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment: EXISTS"
else
    echo "❌ Virtual environment: NOT FOUND"
fi

# Check if Django process is running
DJANGO_PID=$(ps aux | grep 'manage.py runserver' | grep -v grep | awk '{print $2}')

if [ -n "$DJANGO_PID" ]; then
    echo "✅ Django server: RUNNING (PID: $DJANGO_PID)"
    
    # Get port from process
    PORT=$(ps aux | grep 'manage.py runserver' | grep -v grep | sed 's/.*runserver.*:\([0-9]*\).*/\1/')
    if [ -n "$PORT" ]; then
        echo "🌐 Server port: $PORT"
        echo "🌐 URL: http://checkin.taylaibui.vn:$PORT"
    fi
else
    echo "❌ Django server: NOT RUNNING"
fi

# Check database
if [ -f "data/db_test.sqlite3" ]; then
    echo "✅ Database: EXISTS"
    DB_SIZE=$(du -h data/db_test.sqlite3 | cut -f1)
    echo "📊 Database size: $DB_SIZE"
else
    echo "❌ Database: NOT FOUND"
fi

# Check static files
if [ -d "staticfiles" ]; then
    STATIC_COUNT=$(find staticfiles -type f | wc -l)
    echo "✅ Static files: $STATIC_COUNT files"
else
    echo "❌ Static files: NOT FOUND"
fi

echo "=================================="
STATUSEOF
    
    chmod +x status_server.sh
    
    print_success "Status script created"
    
    # Final success message
    echo ""
    print_header "🎉 Setup Completed Successfully!"
    
    echo -e "${GREEN}✅ NOV-RECO Check-in System is ready!${NC}"
    echo ""
    echo -e "${BLUE}📋 Available commands:${NC}"
    echo -e "${YELLOW}   ./start_server.sh          ${NC}# Start server on port 8000"
    echo -e "${YELLOW}   ./start_server.sh 8080     ${NC}# Start server on port 8080"
    echo -e "${YELLOW}   ./stop_server.sh           ${NC}# Stop server"
    echo -e "${YELLOW}   ./status_server.sh         ${NC}# Check server status"
    echo ""
    echo -e "${BLUE}🌐 URLs (after starting server):${NC}"
    echo -e "${GREEN}   Website: http://checkin.taylaibui.vn:8000${NC}"
    echo -e "${GREEN}   Admin:   http://checkin.taylaibui.vn:8000/admin${NC}"
    echo ""
    echo -e "${BLUE}🔑 Login credentials:${NC}"
    echo -e "${GREEN}   Username: admin${NC}"
    echo -e "${GREEN}   Password: admin123${NC}"
    echo ""
    echo -e "${YELLOW}🚀 To start the server now, run:${NC}"
    echo -e "${GREEN}   ./start_server.sh${NC}"
    echo ""
}

# Run main function
main "$@"
