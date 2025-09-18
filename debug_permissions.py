#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.append('.')
django.setup()

from users.models import User

# Kiểm tra user superadmin
try:
    u = User.objects.get(username='superadmin')
    print("=== USER SUPERADMIN DEBUG ===")
    print(f"Username: {u.username}")
    print(f"Role: {u.role}")
    print(f"Is superuser: {u.is_superuser}")
    print(f"Is staff: {u.is_staff}")
    print(f"is_admin(): {u.is_admin()}")
    print(f"is_admin_user property: {u.is_admin_user}")
    print(f"Groups: {[g.name for g in u.groups.all()]}")
    print()
    
    # Kiểm tra các user khác
    for username in ['quanly', 'thuky', 'nhanvien1']:
        try:
            user = User.objects.get(username=username)
            print(f"=== USER {username.upper()} ===")
            print(f"Role: {user.role}")
            print(f"Is superuser: {user.is_superuser}")
            print(f"is_admin(): {user.is_admin()}")
            print(f"is_manager(): {user.is_manager()}")
            print(f"is_employee(): {user.is_employee()}")
            print()
        except User.DoesNotExist:
            print(f"User {username} not found")
            
except User.DoesNotExist:
    print("User superadmin not found!")
