#!/bin/bash
# Script to setup test data for different environments

set -e

ENVIRONMENT=$1
PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")" 2>/dev/null || dirname "$(dirname "$0")")

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 [local|test|production]"
    echo ""
    echo "Examples:"
    echo "  $0 local      # Create test data for local development"
    echo "  $0 test       # Create test data for test server"
    echo "  $0 production # Create minimal data for production"
    exit 1
fi

print_status "🚀 Setting up test data for $ENVIRONMENT environment..."

cd "$PROJECT_DIR"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# For server environments, ensure we're using the correct user
if [ "$ENVIRONMENT" != "local" ]; then
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root or with sudo for server environments"
        exit 1
    fi
    
    # Set environment file
    print_status "Setting environment configuration..."
    cp "config/$ENVIRONMENT.env" ".env"
    
    # Run as www-data user
    print_status "Running test data creation as www-data user..."
    sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python scripts/create-test-data.py $ENVIRONMENT
else
    # Local environment
    if [ -f "venv/bin/activate" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    print_status "Running test data creation for local environment..."
    python scripts/create-test-data.py $ENVIRONMENT
fi

print_success "✅ Test data setup completed for $ENVIRONMENT environment!"
