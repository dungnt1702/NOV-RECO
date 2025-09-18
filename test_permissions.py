#!/usr/bin/env python
"""
Simple test script to check user permissions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.append('.')
django.setup()

from users.models import User, UserRole

print("=== TESTING USER PERMISSIONS ===")

try:
    # Test superadmin user
    u = User.objects.get(username='superadmin')
    print(f"\n👤 User: {u.username}")
    print(f"📧 Email: {u.email}")
    print(f"🏷️ Role: {u.role}")
    print(f"⭐ Is superuser: {u.is_superuser}")
    print(f"👨‍💼 Is staff: {u.is_staff}")
    print(f"🔑 Is admin(): {u.is_admin()}")
    print(f"🔑 Is admin_user property: {u.is_admin_user}")
    print(f"👥 Groups: {[g.name for g in u.groups.all()]}")
    
    # Test role constants
    print(f"\n🔍 UserRole.ADMIN: '{UserRole.ADMIN}'")
    print(f"🔍 User role == UserRole.ADMIN: {u.role == UserRole.ADMIN}")
    print(f"🔍 User role type: {type(u.role)}")
    print(f"🔍 UserRole.ADMIN type: {type(UserRole.ADMIN)}")
    
    print("\n✅ All tests completed!")
    
except User.DoesNotExist:
    print("❌ User 'superadmin' not found!")
except Exception as e:
    print(f"❌ Error: {e}")
