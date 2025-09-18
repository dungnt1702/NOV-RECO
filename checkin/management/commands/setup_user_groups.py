from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User
from checkin.models import Area, Checkin


class Command(BaseCommand):
    help = 'Setup user groups and permissions'

    def handle(self, *args, **options):
        # Tạo các nhóm người dùng
        groups_data = {
            'Super Admin': {
                'description': 'Toàn quyền hệ thống',
                'permissions': 'all'
            },
            'Quản lý': {
                'description': 'Xem và sửa toàn bộ',
                'permissions': [
                    # User permissions
                    'add_user', 'change_user', 'view_user',
                    # Area permissions
                    'add_area', 'change_area', 'delete_area', 'view_area',
                    # Checkin permissions
                    'add_checkin', 'change_checkin', 'delete_checkin', 'view_checkin',
                ]
            },
            'Thư ký': {
                'description': 'Xem và sửa toàn bộ',
                'permissions': [
                    # User permissions (view only)
                    'view_user',
                    # Area permissions
                    'add_area', 'change_area', 'view_area',
                    # Checkin permissions
                    'add_checkin', 'change_checkin', 'view_checkin',
                ]
            },
            'Nhân viên': {
                'description': 'Xem và checkin',
                'permissions': [
                    # Area permissions (view only)
                    'view_area',
                    # Checkin permissions (add and view own)
                    'add_checkin', 'view_checkin',
                ]
            }
        }

        for group_name, group_info in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created group: {group_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group already exists: {group_name}')
                )

            # Clear existing permissions
            group.permissions.clear()

            if group_info['permissions'] == 'all':
                # Super Admin gets all permissions
                if group_name == 'Super Admin':
                    # Make user superuser
                    group.user_set.update(is_superuser=True, is_staff=True)
                    self.stdout.write(
                        self.style.SUCCESS(f'Super Admin users updated')
                    )
            else:
                # Add specific permissions
                for perm_codename in group_info['permissions']:
                    try:
                        # Try to find permission in different content types
                        permission = None
                        
                        # Check User model permissions
                        user_ct = ContentType.objects.get_for_model(User)
                        try:
                            permission = Permission.objects.get(
                                codename=perm_codename,
                                content_type=user_ct
                            )
                        except Permission.DoesNotExist:
                            pass
                        
                        # Check Area model permissions
                        if not permission:
                            area_ct = ContentType.objects.get_for_model(Area)
                            try:
                                permission = Permission.objects.get(
                                    codename=perm_codename,
                                    content_type=area_ct
                                )
                            except Permission.DoesNotExist:
                                pass
                        
                        # Check Checkin model permissions
                        if not permission:
                            checkin_ct = ContentType.objects.get_for_model(Checkin)
                            try:
                                permission = Permission.objects.get(
                                    codename=perm_codename,
                                    content_type=checkin_ct
                                )
                            except Permission.DoesNotExist:
                                pass
                        
                        if permission:
                            group.permissions.add(permission)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Added permission {perm_codename} to {group_name}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Permission not found: {perm_codename}'
                                )
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error adding permission {perm_codename}: {str(e)}'
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS('Successfully setup user groups and permissions!')
        )
