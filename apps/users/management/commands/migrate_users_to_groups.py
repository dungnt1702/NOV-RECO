from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = 'Migrate users from role-based to group-based permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Mapping from old roles to new groups
        role_to_group_mapping = {
            UserRole.ADMIN: 'Admin',
            UserRole.MANAGER: 'Manager', 
            UserRole.HCNS: 'HR',
            UserRole.EMPLOYEE: 'Employee',
        }
        
        # Get all groups
        groups = {group.name: group for group in Group.objects.all()}
        
        # Process each user
        migrated_count = 0
        error_count = 0
        
        for user in User.objects.all():
            try:
                # Skip superusers - they already have all permissions
                if user.is_superuser:
                    if not dry_run:
                        # Add to Super Admin group
                        super_admin_group = groups.get('Super Admin')
                        if super_admin_group:
                            user.groups.add(super_admin_group)
                    self.stdout.write(f'Skipped superuser: {user.username}')
                    continue
                
                # Get the group name for this user's role
                group_name = role_to_group_mapping.get(user.role)
                
                if not group_name:
                    self.stdout.write(
                        self.style.WARNING(f'Unknown role for user {user.username}: {user.role}')
                    )
                    error_count += 1
                    continue
                
                # Get the group
                group = groups.get(group_name)
                if not group:
                    self.stdout.write(
                        self.style.ERROR(f'Group not found: {group_name}')
                    )
                    error_count += 1
                    continue
                
                if dry_run:
                    self.stdout.write(
                        f'Would migrate {user.username} ({user.role}) -> {group_name}'
                    )
                else:
                    # Clear existing groups and add new group
                    user.groups.clear()
                    user.groups.add(group)
                    self.stdout.write(
                        f'Migrated {user.username} ({user.role}) -> {group_name}'
                    )
                
                migrated_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating user {user.username}: {str(e)}')
                )
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MIGRATION SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Users processed: {migrated_count + error_count}')
        self.stdout.write(f'Successfully migrated: {migrated_count}')
        self.stdout.write(f'Errors: {error_count}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nThis was a DRY RUN. Run without --dry-run to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nMigration completed successfully!')
            )
