from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Test the new permission system"

    def handle(self, *args, **options):
        self.stdout.write("Testing permission system...")

        # Test groups
        self.stdout.write("\n=== GROUPS ===")
        groups = Group.objects.all()
        for group in groups:
            self.stdout.write(f"Group: {group.name}")
            permissions = group.permissions.all()
            for perm in permissions:
                self.stdout.write(f"  - {perm.codename}: {perm.name}")

        # Test users
        self.stdout.write("\n=== USERS ===")
        users = User.objects.all()[:5]  # Test first 5 users
        for user in users:
            self.stdout.write(f"\nUser: {user.username} ({user.get_full_name()})")
            self.stdout.write(f"  - Is Superuser: {user.is_superuser}")
            self.stdout.write(f"  - Groups: {[g.name for g in user.groups.all()]}")

            # Test new permission methods
            self.stdout.write(f"  - Can manage users: {user.can_manage_users_new()}")
            self.stdout.write(f"  - Can view users: {user.can_view_users_new()}")
            self.stdout.write(
                f"  - Can manage checkins: {user.can_manage_checkins_new()}"
            )
            self.stdout.write(
                f"  - Can view all checkins: {user.can_view_all_checkins_new()}"
            )
            self.stdout.write(f"  - Can manage areas: {user.can_manage_areas_new()}")
            self.stdout.write(f"  - Can view areas: {user.can_view_areas_new()}")

            # Test group methods
            self.stdout.write(f"  - Is Super Admin: {user.is_super_admin()}")
            self.stdout.write(f"  - Is Admin: {user.is_admin_user_new()}")
            self.stdout.write(f"  - Is Manager: {user.is_manager_user_new()}")
            self.stdout.write(f"  - Is HR: {user.is_hr_user()}")
            self.stdout.write(f"  - Is Secretary: {user.is_secretary_user()}")
            self.stdout.write(f"  - Is Employee: {user.is_employee_user_new()}")

        self.stdout.write("\n=== PERMISSION SUMMARY ===")
        total_users = User.objects.count()
        super_admins = User.objects.filter(groups__name="Super Admin").count()
        admins = User.objects.filter(groups__name="Admin").count()
        managers = User.objects.filter(groups__name="Manager").count()
        hr_users = User.objects.filter(groups__name="HR").count()
        secretaries = User.objects.filter(groups__name="Secretary").count()
        employees = User.objects.filter(groups__name="Employee").count()

        self.stdout.write(f"Total Users: {total_users}")
        self.stdout.write(f"Super Admins: {super_admins}")
        self.stdout.write(f"Admins: {admins}")
        self.stdout.write(f"Managers: {managers}")
        self.stdout.write(f"HR Users: {hr_users}")
        self.stdout.write(f"Secretaries: {secretaries}")
        self.stdout.write(f"Employees: {employees}")

        self.stdout.write(self.style.SUCCESS("\nPermission system test completed!"))
