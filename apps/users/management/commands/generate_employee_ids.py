from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Generate employee_id for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        users = User.objects.filter(employee_id__isnull=True)
        
        if not users.exists():
            self.stdout.write(
                self.style.SUCCESS('All users already have employee_id')
            )
            return
        
        self.stdout.write(f'Found {users.count()} users without employee_id')
        
        for user in users:
            # Generate employee_id based on user ID with prefix
            employee_id = f'EMP{user.id:06d}'
            
            if dry_run:
                self.stdout.write(
                    f'Would set employee_id for {user.username} ({user.get_full_name()}) to {employee_id}'
                )
            else:
                user.employee_id = employee_id
                user.save()
                self.stdout.write(
                    f'Set employee_id for {user.username} ({user.get_full_name()}) to {employee_id}'
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Dry run completed. Use --dry-run=False to apply changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Successfully generated employee_id for all users')
            )
