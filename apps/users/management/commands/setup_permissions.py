from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User
from apps.checkin.models import Checkin
from apps.area.models import Area


class Command(BaseCommand):
    help = 'Setup groups and permissions for NOV-RECO system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up groups and permissions...')
        
        # Create groups
        groups = self.create_groups()
        
        # Assign permissions to groups
        self.assign_permissions(groups)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup groups and permissions!')
        )

    def create_groups(self):
        """Create the 5 main groups"""
        groups = {}
        
        group_data = [
            ('super_admin', 'Super Admin', 'Toàn quyền hệ thống'),
            ('admin', 'Admin', 'Quản trị viên'),
            ('manager', 'Manager', 'Quản lý'),
            ('hr', 'HR', 'Nhân sự'),
            ('secretary', 'Secretary', 'Thư ký'),
            ('employee', 'Employee', 'Nhân viên'),
        ]
        
        for codename, name, description in group_data:
            group, created = Group.objects.get_or_create(
                name=name,
                defaults={'name': name}
            )
            groups[codename] = group
            
            if created:
                self.stdout.write(f'Created group: {name}')
            else:
                self.stdout.write(f'Group already exists: {name}')
        
        return groups

    def assign_permissions(self, groups):
        """Assign permissions to groups based on their roles"""
        
        # Get content types
        user_ct = ContentType.objects.get_for_model(User)
        checkin_ct = ContentType.objects.get_for_model(Checkin)
        area_ct = ContentType.objects.get_for_model(Area)
        
        # Super Admin - All permissions
        super_admin_perms = Permission.objects.all()
        groups['super_admin'].permissions.set(super_admin_perms)
        self.stdout.write('Assigned all permissions to Super Admin')
        
        # Admin - All permissions except super admin management
        admin_perms = Permission.objects.exclude(
            codename__in=['can_manage_roles', 'can_assign_roles']
        ).exclude(
            user__is_superuser=True  # Exclude superuser management
        )
        groups['admin'].permissions.set(admin_perms)
        self.stdout.write('Assigned admin permissions to Admin')
        
        # Manager - User management, checkin, area (no role management)
        manager_perms = Permission.objects.filter(
            codename__in=[
                # User management
                'can_manage_users', 'can_view_users', 'can_create_users', 
                'can_edit_users', 'can_delete_users',
                # Department management
                'can_manage_departments', 'can_view_departments', 
                'can_create_departments', 'can_edit_departments', 'can_delete_departments',
                # Checkin management
                'can_manage_checkins', 'can_view_checkins', 'can_view_all_checkins',
                'can_view_checkin_reports', 'can_export_checkin_data',
                # Area management
                'can_manage_areas', 'can_view_areas', 'can_create_areas', 
                'can_edit_areas', 'can_delete_areas', 'can_activate_areas',
                # Basic permissions
                'add_user', 'change_user', 'view_user', 'delete_user',
                'add_checkin', 'change_checkin', 'view_checkin', 'delete_checkin',
                'add_area', 'change_area', 'view_area', 'delete_area',
            ]
        )
        groups['manager'].permissions.set(manager_perms)
        self.stdout.write('Assigned manager permissions to Manager')
        
        # HR - User management, department, area
        hr_perms = Permission.objects.filter(
            codename__in=[
                # User management
                'can_manage_users', 'can_view_users', 'can_create_users', 
                'can_edit_users', 'can_delete_users',
                # Department management
                'can_manage_departments', 'can_view_departments', 
                'can_create_departments', 'can_edit_departments', 'can_delete_departments',
                # Area management
                'can_manage_areas', 'can_view_areas', 'can_create_areas', 
                'can_edit_areas', 'can_delete_areas', 'can_activate_areas',
                # Basic permissions
                'add_user', 'change_user', 'view_user', 'delete_user',
                'add_area', 'change_area', 'view_area', 'delete_area',
            ]
        )
        groups['hr'].permissions.set(hr_perms)
        self.stdout.write('Assigned HR permissions to HR')
        
        # Secretary - Checkin and area management
        secretary_perms = Permission.objects.filter(
            codename__in=[
                # Checkin management
                'can_manage_checkins', 'can_view_checkins', 'can_view_all_checkins',
                'can_view_checkin_reports', 'can_export_checkin_data',
                # Area management
                'can_manage_areas', 'can_view_areas', 'can_create_areas', 
                'can_edit_areas', 'can_delete_areas', 'can_activate_areas',
                # Basic permissions
                'add_checkin', 'change_checkin', 'view_checkin', 'delete_checkin',
                'add_area', 'change_area', 'view_area', 'delete_area',
            ]
        )
        groups['secretary'].permissions.set(secretary_perms)
        self.stdout.write('Assigned secretary permissions to Secretary')
        
        # Employee - Basic checkin and own data
        employee_perms = Permission.objects.filter(
            codename__in=[
                # Own checkin
                'can_create_checkins', 'can_view_own_checkins',
                # View areas
                'can_view_areas',
                # Basic permissions
                'add_checkin', 'view_checkin', 'view_area',
            ]
        )
        groups['employee'].permissions.set(employee_perms)
        self.stdout.write('Assigned employee permissions to Employee')
        
        return groups
