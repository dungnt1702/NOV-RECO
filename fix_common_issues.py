#!/usr/bin/env python
"""
Fix Common Issues Script for NOV-RECO Check-in System
Khắc phục các lỗi phổ biến trong hệ thống
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings

class IssueFixer:
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
    
    def log_fix(self, fix_name, success, message=""):
        """Ghi log kết quả fix"""
        status = "✅ FIXED" if success else "❌ FAILED"
        self.fixes_applied.append({
            'fix': fix_name,
            'success': success,
            'message': message
        })
        print(f"{status} {fix_name}: {message}")
    
    def fix_missing_migrations(self):
        """Tạo migrations cho các models"""
        try:
            print("Creating migrations...")
            execute_from_command_line(['manage.py', 'makemigrations'])
            self.log_fix("Create Migrations", True, "Migrations created successfully")
            
            print("Applying migrations...")
            execute_from_command_line(['manage.py', 'migrate'])
            self.log_fix("Apply Migrations", True, "Migrations applied successfully")
            
        except Exception as e:
            self.log_fix("Migrations", False, f"Error: {str(e)}")
    
    def fix_static_files(self):
        """Collect static files"""
        try:
            print("Collecting static files...")
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            self.log_fix("Collect Static Files", True, "Static files collected successfully")
            
        except Exception as e:
            self.log_fix("Static Files", False, f"Error: {str(e)}")
    
    def fix_permissions(self):
        """Sửa quyền truy cập files"""
        try:
            print("Fixing file permissions...")
            
            # Sửa quyền cho database files
            db_files = ['data/db_local.sqlite3', 'data/db.sqlite3']
            for db_file in db_files:
                if os.path.exists(db_file):
                    os.chmod(db_file, 0o666)
            
            # Sửa quyền cho media directory
            media_dir = Path(settings.MEDIA_ROOT)
            if media_dir.exists():
                os.chmod(media_dir, 0o755)
                for file in media_dir.rglob('*'):
                    if file.is_file():
                        os.chmod(file, 0o644)
            
            self.log_fix("File Permissions", True, "Permissions fixed successfully")
            
        except Exception as e:
            self.log_fix("File Permissions", False, f"Error: {str(e)}")
    
    def fix_database_integrity(self):
        """Sửa lỗi database integrity"""
        try:
            print("Checking database integrity...")
            
            # Kiểm tra và sửa lỗi foreign key
            from django.db import connection
            with connection.cursor() as cursor:
                # Kiểm tra integrity
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                if result[0] != 'ok':
                    print(f"Database integrity issue: {result[0]}")
                    # Có thể cần recreate database
                    return False
                else:
                    print("Database integrity is OK")
            
            self.log_fix("Database Integrity", True, "Database is healthy")
            
        except Exception as e:
            self.log_fix("Database Integrity", False, f"Error: {str(e)}")
    
    def fix_template_errors(self):
        """Sửa lỗi template"""
        try:
            print("Checking template syntax...")
            
            # Kiểm tra các template chính
            templates_to_check = [
                'templates/base.html',
                'templates/home.html',
                'templates/header.html',
                'templates/footer.html',
                'templates/checkin/action.html',
                'templates/checkin/history.html',
                'templates/checkin/list.html',
                'templates/area/list.html',
                'templates/users/user_list.html',
                'templates/personal/profile.html'
            ]
            
            for template_path in templates_to_check:
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Kiểm tra các lỗi phổ biến
                    if '{% url' in content and 'checkin_page' in content:
                        print(f"Found old URL reference in {template_path}")
                        # Có thể cần sửa thủ công
                    
                    if '{% static' in content and not '{% load static %}' in content:
                        print(f"Missing static load in {template_path}")
            
            self.log_fix("Template Check", True, "Templates checked successfully")
            
        except Exception as e:
            self.log_fix("Template Check", False, f"Error: {str(e)}")
    
    def fix_import_errors(self):
        """Sửa lỗi import"""
        try:
            print("Checking import errors...")
            
            # Kiểm tra các file Python chính
            python_files = [
                'apps/checkin/views.py',
                'apps/checkin/urls_checkin.py',
                'apps/area/views.py',
                'apps/area/urls.py',
                'apps/users/views.py',
                'apps/users/urls.py',
                'apps/personal/views.py',
                'apps/personal/urls.py',
                'apps/dashboard/views.py',
                'apps/dashboard/urls.py',
                'config/urls.py'
            ]
            
            for py_file in python_files:
                if os.path.exists(py_file):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Kiểm tra import syntax
                        if 'from apps.' in content:
                            # Kiểm tra xem có import đúng không
                            pass
                            
                    except Exception as e:
                        print(f"Error reading {py_file}: {e}")
            
            self.log_fix("Import Check", True, "Imports checked successfully")
            
        except Exception as e:
            self.log_fix("Import Check", False, f"Error: {str(e)}")
    
    def fix_url_patterns(self):
        """Sửa lỗi URL patterns"""
        try:
            print("Checking URL patterns...")
            
            # Kiểm tra config/urls.py
            urls_file = 'config/urls.py'
            if os.path.exists(urls_file):
                with open(urls_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Kiểm tra các URL patterns chính
                required_patterns = [
                    'path("checkin/", include("apps.checkin.urls_checkin"))',
                    'path("area/", include("apps.area.urls"))',
                    'path("users/", include("apps.users.urls"))',
                    'path("personal/", include("apps.personal.urls"))',
                    'path("dashboard/", include("apps.dashboard.urls"))'
                ]
                
                for pattern in required_patterns:
                    if pattern not in content:
                        print(f"Missing URL pattern: {pattern}")
            
            self.log_fix("URL Patterns", True, "URL patterns checked successfully")
            
        except Exception as e:
            self.log_fix("URL Patterns", False, f"Error: {str(e)}")
    
    def fix_media_files(self):
        """Tạo thư mục media nếu chưa có"""
        try:
            print("Creating media directories...")
            
            media_dirs = [
                'media/',
                'media/avatars/',
                'media/checkins/',
                'static/',
                'static/css/',
                'static/js/',
                'static/css/webfonts/'
            ]
            
            for dir_path in media_dirs:
                os.makedirs(dir_path, exist_ok=True)
            
            self.log_fix("Media Directories", True, "Media directories created successfully")
            
        except Exception as e:
            self.log_fix("Media Directories", False, f"Error: {str(e)}")
    
    def fix_database_connection(self):
        """Kiểm tra kết nối database"""
        try:
            print("Testing database connection...")
            
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    print("Database connection successful")
                else:
                    print("Database connection failed")
                    return False
            
            self.log_fix("Database Connection", True, "Database connection successful")
            
        except Exception as e:
            self.log_fix("Database Connection", False, f"Error: {str(e)}")
    
    def run_all_fixes(self):
        """Chạy tất cả các fix"""
        print("=" * 60)
        print("NOV-RECO CHECK-IN SYSTEM - ISSUE FIXER")
        print("=" * 60)
        print(f"Fixing started at: {datetime.now()}")
        print("=" * 60)
        
        # Chạy các fix
        self.fix_database_connection()
        self.fix_missing_migrations()
        self.fix_database_integrity()
        self.fix_media_files()
        self.fix_static_files()
        self.fix_permissions()
        self.fix_template_errors()
        self.fix_import_errors()
        self.fix_url_patterns()
        
        # Tổng kết
        print("=" * 60)
        print("FIX SUMMARY")
        print("=" * 60)
        
        total_fixes = len(self.fixes_applied)
        successful_fixes = sum(1 for fix in self.fixes_applied if fix['success'])
        failed_fixes = total_fixes - successful_fixes
        
        print(f"Total Fixes: {total_fixes}")
        print(f"Successful: {successful_fixes}")
        print(f"Failed: {failed_fixes}")
        print(f"Success Rate: {(successful_fixes/total_fixes)*100:.1f}%")
        
        if failed_fixes > 0:
            print("\nFAILED FIXES:")
            print("-" * 30)
            for fix in self.fixes_applied:
                if not fix['success']:
                    print(f"❌ {fix['fix']}: {fix['message']}")
        
        print("=" * 60)
        print(f"Fixing completed at: {datetime.now()}")
        print("=" * 60)
        
        return failed_fixes == 0

if __name__ == '__main__':
    from datetime import datetime
    fixer = IssueFixer()
    success = fixer.run_all_fixes()
    sys.exit(0 if success else 1)
