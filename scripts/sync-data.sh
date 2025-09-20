#!/bin/bash
# Data Synchronization Script
# Sync data from local to production or between environments

set -e

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

# Configuration
BACKUP_DIR="data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

print_status "NOV-RECO Data Synchronization Tool"
echo ""
echo "Options:"
echo "1. Export local data to file"
echo "2. Import data from file"
echo "3. Create sample data"
echo "4. Backup current database"
echo "5. Reset database (careful!)"
echo ""
read -p "Choose option (1-5): " choice

case $choice in
    1)
        print_status "Exporting local data..."
        python manage.py dumpdata \
            --natural-foreign \
            --natural-primary \
            --exclude contenttypes \
            --exclude auth.Permission \
            --exclude sessions.Session \
            --exclude admin.LogEntry \
            --indent 2 \
            > $BACKUP_DIR/data_export_$DATE.json
        print_success "Data exported to: $BACKUP_DIR/data_export_$DATE.json"
        ;;
    2)
        echo ""
        ls -la $BACKUP_DIR/*.json 2>/dev/null || echo "No backup files found"
        echo ""
        read -p "Enter backup file path: " backup_file
        if [ -f "$backup_file" ]; then
            print_warning "This will overwrite existing data. Continue? (y/N)"
            read -p "Confirm: " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                print_status "Importing data from $backup_file..."
                python manage.py loaddata "$backup_file"
                print_success "Data imported successfully!"
            else
                print_status "Import cancelled."
            fi
        else
            print_error "File not found: $backup_file"
        fi
        ;;
    3)
        print_status "Creating sample data..."
        python manage.py shell -c "
# Create sample areas
from checkin.models import Area
from users.models import User, Department
from django.contrib.auth import get_user_model

# Create departments
dept_it, _ = Department.objects.get_or_create(name='IT')
dept_sales, _ = Department.objects.get_or_create(name='Sales')
dept_hr, _ = Department.objects.get_or_create(name='HR')

# Create sample users
User = get_user_model()
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@nov-reco.com',
        'first_name': 'Admin',
        'last_name': 'System',
        'role': 'admin',
        'department': dept_it,
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()

manager, created = User.objects.get_or_create(
    username='manager1',
    defaults={
        'email': 'manager@nov-reco.com',
        'first_name': 'Nguyễn',
        'last_name': 'Văn A',
        'role': 'manager',
        'department': dept_sales,
        'employee_id': 'EMP001'
    }
)
if created:
    manager.set_password('manager123')
    manager.save()

employee, created = User.objects.get_or_create(
    username='employee1',
    defaults={
        'email': 'employee@nov-reco.com',
        'first_name': 'Trần',
        'last_name': 'Thị B',
        'role': 'employee',
        'department': dept_hr,
        'employee_id': 'EMP002'
    }
)
if created:
    employee.set_password('employee123')
    employee.save()

# Create sample areas
Area.objects.get_or_create(
    name='Văn phòng chính',
    defaults={
        'latitude': 10.7769,
        'longitude': 106.7009,
        'radius': 100,
        'address': '123 Nguyễn Huệ, Quận 1, TP.HCM',
        'created_by': admin
    }
)

Area.objects.get_or_create(
    name='Chi nhánh Quận 7',
    defaults={
        'latitude': 10.7308,
        'longitude': 106.7194,
        'radius': 50,
        'address': '456 Nguyễn Thị Thập, Quận 7, TP.HCM',
        'created_by': admin
    }
)

print('Sample data created successfully!')
print('Users created:')
print('- admin / admin123 (Admin)')
print('- manager1 / manager123 (Manager)')
print('- employee1 / employee123 (Employee)')
"
        print_success "Sample data created!"
        ;;
    4)
        print_status "Creating database backup..."
        python manage.py dumpdata \
            --natural-foreign \
            --natural-primary \
            --exclude contenttypes \
            --exclude auth.Permission \
            --exclude sessions.Session \
            --exclude admin.LogEntry \
            --indent 2 \
            > $BACKUP_DIR/backup_$DATE.json
        print_success "Backup created: $BACKUP_DIR/backup_$DATE.json"
        ;;
    5)
        print_warning "⚠️  This will DELETE ALL DATA in the database!"
        print_warning "Make sure you have a backup first."
        echo ""
        read -p "Type 'DELETE ALL DATA' to confirm: " confirm
        if [ "$confirm" = "DELETE ALL DATA" ]; then
            print_status "Resetting database..."
            rm -f data/db.sqlite3
            python manage.py migrate
            print_success "Database reset completed!"
            print_status "Run option 3 to create sample data."
        else
            print_status "Reset cancelled."
        fi
        ;;
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo ""
print_success "Operation completed!"
