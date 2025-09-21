#!/bin/bash

# NOV-RECO Simple Server - Minimal setup without allauth
# For Python 3.6 shared hosting

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

# Install minimal packages
install_packages() {
    print_status "📦 Installing minimal Django packages..."
    
    # Add pip to PATH
    export PATH="/var/www/vhosts/taylaibui.vn/.local/bin:$PATH"
    
    # Install pip3 if needed
    if ! command -v pip3 &> /dev/null; then
        curl -s https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py
        python3 get-pip.py --user --quiet
        rm -f get-pip.py
    fi
    
    # Install only essential packages
    pip3 install --user --quiet "Django==3.2.25"
    pip3 install --user --quiet "djangorestframework==3.14.0"
    pip3 install --user --quiet "Pillow==8.4.0"
    
    print_success "Essential packages installed"
}

# Create minimal settings
create_minimal_settings() {
    print_status "⚙️ Creating minimal settings..."
    
    # Backup original settings
    cp project/settings.py project/settings_backup.py
    
    # Create minimal settings without allauth
    cat > project/settings_minimal.py << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Configuration
ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "test")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "test-secret-key-minimal")
DEBUG = True
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "checkin.taylaibui.vn,localhost,127.0.0.1,0.0.0.0").split(",")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'checkin',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
DATABASE_NAME = os.environ.get("DATABASE_NAME", "data/db_test.sqlite3")
if not DATABASE_NAME.startswith("/"):
    DATABASE_NAME = BASE_DIR / DATABASE_NAME

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_NAME,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
EOF
    
    print_success "Minimal settings created"
}

# Setup Django with minimal settings
setup_django_minimal() {
    print_status "🗄️ Setting up Django with minimal settings..."
    
    # Create directories
    mkdir -p data logs media staticfiles
    
    # Set environment variables
    export DJANGO_ENVIRONMENT=test
    export DATABASE_NAME=data/db_test.sqlite3
    export ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1,0.0.0.0"
    export DJANGO_SETTINGS_MODULE=project.settings_minimal
    
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

# Start server with minimal settings
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
    export DJANGO_SETTINGS_MODULE=project.settings_minimal
    
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

# Check if packages are installed
check_packages() {
    if python3 -c "import django" 2>/dev/null; then
        DJANGO_VERSION=$(python3 -c "import django; print(django.get_version())")
        print_success "Django $DJANGO_VERSION installed"
        return 0
    else
        print_info "Django not installed"
        return 1
    fi
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
        echo -e "${BLUE}🚀 NOV-RECO Simple Setup & Start${NC}"
        echo "=================================="
        
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
        
        # Install packages if needed
        if ! check_packages; then
            install_packages
            echo ""
        fi
        
        # Create minimal settings
        create_minimal_settings
        echo ""
        
        # Setup Django
        setup_django_minimal
        echo ""
        
        # Start server
        start_server ${2:-$DEFAULT_PORT}
        ;;
    *)
        echo -e "${BLUE}🚀 NOV-RECO Simple Server Manager${NC}"
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
        echo ""
        echo -e "${YELLOW}Note: Uses minimal Django setup without allauth${NC}"
        ;;
esac
