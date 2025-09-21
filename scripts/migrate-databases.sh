#!/bin/bash
# Script to migrate databases across environments

set -e

ENVIRONMENT=$1
ACTION=$2

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_help() {
    echo "Usage: $0 <environment> <action>"
    echo "Environments: local, test, production"
    echo "Actions:"
    echo "  migrate     - Run Django migrations"
    echo "  backup      - Backup database"
    echo "  restore     - Restore database from backup"
    echo "  reset       - Reset database (WARNING: destroys data)"
    echo "  status      - Show migration status"
    echo ""
    echo "Examples:"
    echo "  $0 local migrate      # Run migrations on local database"
    echo "  $0 test backup        # Backup test database"
    echo "  $0 production migrate # Run migrations on production database"
}

if [ -z "$ENVIRONMENT" ] || [ -z "$ACTION" ]; then
    print_help
    exit 1
fi

# Set paths based on environment
case "$ENVIRONMENT" in
    "local")
        PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
        DB_PATH="$PROJECT_DIR/data/db_local.sqlite3"
        ENV_FILE="$PROJECT_DIR/config/local.env"
        ;;
    "test")
        PROJECT_DIR="/var/www/checkin.taylaibui.vn"
        DB_PATH="/var/www/checkin.taylaibui.vn/data/db_test.sqlite3"
        ENV_FILE="$PROJECT_DIR/config/test.env"
        ;;
    "production")
        PROJECT_DIR="/var/www/checkin.taylaibui.vn"
        DB_PATH="/var/www/checkin.taylaibui.vn/data/db.sqlite3"
        ENV_FILE="$PROJECT_DIR/config/production.env"
        ;;
    *)
        print_error "Invalid environment: $ENVIRONMENT"
        print_help
        exit 1
        ;;
esac

print_status "Environment: $ENVIRONMENT"
print_status "Database: $DB_PATH"
print_status "Action: $ACTION"

cd "$PROJECT_DIR"

case "$ACTION" in
    "migrate")
        print_status "Running migrations for $ENVIRONMENT environment..."
        
        # Copy environment file
        cp "$ENV_FILE" ".env"
        
        # Run migrations
        if [ "$ENVIRONMENT" == "local" ]; then
            ./venv/bin/python manage.py migrate
        else
            sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py migrate
        fi
        
        print_success "Migrations completed for $ENVIRONMENT"
        ;;
        
    "backup")
        print_status "Backing up $ENVIRONMENT database..."
        
        BACKUP_DIR="/var/backups/nov-reco/databases"
        TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
        
        if [ "$ENVIRONMENT" == "local" ]; then
            BACKUP_DIR="./backups/databases"
        fi
        
        mkdir -p "$BACKUP_DIR"
        
        if [ -f "$DB_PATH" ]; then
            cp "$DB_PATH" "$BACKUP_DIR/db_${ENVIRONMENT}_${TIMESTAMP}.sqlite3"
            print_success "Database backed up to: $BACKUP_DIR/db_${ENVIRONMENT}_${TIMESTAMP}.sqlite3"
        else
            print_error "Database file not found: $DB_PATH"
            exit 1
        fi
        ;;
        
    "restore")
        print_status "Available backups for $ENVIRONMENT:"
        
        BACKUP_DIR="/var/backups/nov-reco/databases"
        if [ "$ENVIRONMENT" == "local" ]; then
            BACKUP_DIR="./backups/databases"
        fi
        
        if [ -d "$BACKUP_DIR" ]; then
            ls -la "$BACKUP_DIR"/db_${ENVIRONMENT}_*.sqlite3 2>/dev/null || echo "No backups found"
        else
            print_error "Backup directory not found: $BACKUP_DIR"
            exit 1
        fi
        
        echo "To restore, copy the backup file manually:"
        echo "cp $BACKUP_DIR/db_${ENVIRONMENT}_TIMESTAMP.sqlite3 $DB_PATH"
        ;;
        
    "reset")
        print_error "WARNING: This will destroy all data in $ENVIRONMENT database!"
        echo "To reset database:"
        echo "1. rm $DB_PATH"
        echo "2. $0 $ENVIRONMENT migrate"
        ;;
        
    "status")
        print_status "Migration status for $ENVIRONMENT:"
        
        # Copy environment file
        cp "$ENV_FILE" ".env"
        
        if [ "$ENVIRONMENT" == "local" ]; then
            ./venv/bin/python manage.py showmigrations
        else
            sudo -u www-data DJANGO_ENVIRONMENT=$ENVIRONMENT ./venv/bin/python manage.py showmigrations
        fi
        ;;
        
    *)
        print_error "Invalid action: $ACTION"
        print_help
        exit 1
        ;;
esac
