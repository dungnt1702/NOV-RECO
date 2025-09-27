import random

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Redistribute users to groups according to new requirements"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        # Target distribution
        target_distribution = {
            "Super Admin": 1,
            "Admin": 3,
            "Manager": 5,
            "Secretary": 2,
            "HR": 2,
            "Employee": None,  # Rest will be Employee
        }

        # Get all users
        all_users = list(User.objects.all())
        total_users = len(all_users)

        self.stdout.write(f"Total users: {total_users}")

        # Calculate Employee count
        assigned_count = sum(
            count for count in target_distribution.values() if count is not None
        )
        employee_count = total_users - assigned_count
        target_distribution["Employee"] = employee_count

        self.stdout.write("\nTarget distribution:")
        for group_name, count in target_distribution.items():
            self.stdout.write(f"  {group_name}: {count}")

        # Get groups
        groups = {}
        for group_name in target_distribution.keys():
            try:
                groups[group_name] = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Group "{group_name}" does not exist!')
                )
                return

        # Clear all user groups first
        if not dry_run:
            for user in all_users:
                user.groups.clear()

        # Shuffle users for random distribution
        random.shuffle(all_users)

        # Distribute users
        user_index = 0
        distribution_results = {}

        for group_name, target_count in target_distribution.items():
            if target_count is None:
                continue

            group = groups[group_name]
            assigned_users = []

            # Assign users to this group
            for i in range(target_count):
                if user_index < len(all_users):
                    user = all_users[user_index]
                    assigned_users.append(user)

                    if not dry_run:
                        user.groups.add(group)

                    user_index += 1

            distribution_results[group_name] = {
                "target": target_count,
                "assigned": len(assigned_users),
                "users": assigned_users,
            }

        # Assign remaining users to Employee group
        remaining_users = all_users[user_index:]
        if remaining_users:
            employee_group = groups["Employee"]
            distribution_results["Employee"] = {
                "target": len(remaining_users),
                "assigned": len(remaining_users),
                "users": remaining_users,
            }

            if not dry_run:
                for user in remaining_users:
                    user.groups.add(employee_group)

        # Display results
        self.stdout.write("\nDistribution results:")
        for group_name, result in distribution_results.items():
            self.stdout.write(f"\n{group_name}:")
            self.stdout.write(f'  Target: {result["target"]}')
            self.stdout.write(f'  Assigned: {result["assigned"]}')

            if result["assigned"] <= 10:  # Show usernames if <= 10 users
                usernames = [user.username for user in result["users"]]
                self.stdout.write(f'  Users: {", ".join(usernames)}')
            else:
                self.stdout.write(f'  Users: {result["assigned"]} users assigned')

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS("\nUser redistribution completed successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("\nDry run completed. No changes were made.")
            )
