"""
Management command to update old check-ins with location_id based on coordinates
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.checkin.models import Checkin
from apps.checkin.utils import haversine_m
from apps.location.models import Location


class Command(BaseCommand):
    help = "Update old check-ins with location_id based on coordinates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )
        parser.add_argument(
            "--location-id",
            type=int,
            help="Specific location ID to assign to check-ins",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        specific_location_id = options.get("location_id")

        # Get check-ins without location_id
        checkins_without_location = Checkin.objects.filter(location__isnull=True)

        if not checkins_without_location.exists():
            self.stdout.write(
                self.style.SUCCESS("No check-ins found without location_id")
            )
            return

        self.stdout.write(
            f"Found {checkins_without_location.count()} check-ins without location_id"
        )

        # Get all active locations
        locations = Location.objects.filter(is_active=True)

        if not locations.exists():
            self.stdout.write(self.style.ERROR("No active locations found"))
            return

        self.stdout.write(f"Found {locations.count()} active locations")

        # If specific location ID provided, use only that location
        if specific_location_id:
            try:
                target_location = Location.objects.get(
                    id=specific_location_id, is_active=True
                )
                locations = [target_location]
                self.stdout.write(f"Using specific location: {target_location.name}")
            except Location.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Location with ID {specific_location_id} not found or inactive"
                    )
                )
                return

        updated_count = 0
        not_updated_count = 0

        with transaction.atomic():
            for checkin in checkins_without_location:
                if not checkin.lat or not checkin.lng:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Check-in {checkin.id} has no coordinates, skipping"
                        )
                    )
                    not_updated_count += 1
                    continue

                # Find the closest location within radius
                best_location = None
                min_distance = float("inf")

                for location in locations:
                    distance = haversine_m(
                        location.lat, location.lng, checkin.lat, checkin.lng
                    )

                    # Check if check-in is within location's radius
                    if distance <= location.radius_m and distance < min_distance:
                        best_location = location
                        min_distance = distance

                if best_location:
                    if not dry_run:
                        checkin.location = best_location
                        checkin.save(update_fields=["location"])

                    self.stdout.write(
                        f'{"[DRY RUN] " if dry_run else ""}Check-in {checkin.id}: '
                        f"Assigned to {best_location.name} (distance: {min_distance:.2f}m)"
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Check-in {checkin.id}: No location found within radius "
                            f"(coordinates: {checkin.lat}, {checkin.lng})"
                        )
                    )
                    not_updated_count += 1

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n[DRY RUN] Would update {updated_count} check-ins, "
                    f"{not_updated_count} would remain unassigned"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nUpdated {updated_count} check-ins, "
                    f"{not_updated_count} remain unassigned"
                )
            )

        # Show remaining check-ins without location
        remaining = Checkin.objects.filter(location__isnull=True).count()
        if remaining > 0:
            self.stdout.write(
                self.style.WARNING(f"{remaining} check-ins still without location_id")
            )
