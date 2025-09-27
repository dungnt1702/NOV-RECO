from __future__ import annotations

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.area.models import Area
from apps.checkin.models import Checkin
from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = "Seed demo data: departments (if applicable), users, areas, and checkins"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help=("Delete existing demo objects before seeding"),
        )
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            help="Number of demo employees to create (excluding admin)",
        )
        parser.add_argument(
            "--checkins",
            type=int,
            default=10,
            help="Approximate number of checkins per employee",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["reset"]:
                self.stdout.write(self.style.WARNING("Resetting demo data..."))
                Checkin.objects.all().delete()
                # Keep users but we will ensure demo users are recreated/updated

            admin = self._ensure_admin()
            departments = self._ensure_departments()
            areas = self._ensure_areas()
            users = self._ensure_users(options["users"], departments)
            users_for_checkins = users + [admin]
            self._seed_checkins(users_for_checkins, areas, options["checkins"])

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _ensure_admin(self) -> User:
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "System",
                "last_name": "Admin",
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if not admin.password:
            admin.set_password("admin123")
            admin.save(update_fields=["password"])
        return admin

    def _ensure_departments(self):
        # Department model may or may not exist depending on project.
        try:
            from apps.users.models import Department  # type: ignore

            names = ["HCNS", "Kinh Doanh", "Kỹ Thuật", "Kế Toán"]
            departments = []
            for name in names:
                dept, _ = Department.objects.get_or_create(name=name)
                departments.append(dept)
            return departments
        except Exception:
            return []

    def _ensure_areas(self):
        sample = [
            ("Địa điểm 1", 10.776889, 106.700806, 200),
            ("Địa điểm 2", 10.823099, 106.629662, 250),
            ("Văn phòng", 10.776531, 106.700981, 150),
        ]
        areas: list[Area] = []
        for name, lat, lng, radius in sample:
            area, _ = Area.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} demo",
                    "lat": lat,
                    "lng": lng,
                    "radius_m": radius,
                    "is_active": True,
                },
            )
            # ensure coordinates/radius present even if existed without
            updated = False
            if not area.lat:
                area.lat = lat
                updated = True
            if not area.lng:
                area.lng = lng
                updated = True
            if not area.radius_m:
                area.radius_m = radius
                updated = True
            if updated:
                area.save()
            areas.append(area)
        return areas

    def _ensure_users(self, num_users: int, departments):
        users: list[User] = []
        # Ensure one manager and one HCNS
        presets = [
            ("manager", "Quản", "Lý", UserRole.MANAGER),
            ("hcns", "HC", "NS", UserRole.HCNS),
        ]
        for username, first, last, role in presets:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                    "is_active": True,
                },
            )
            if departments:
                # round-robin departments
                user.department = departments[len(users) % len(departments)]
            if not user.password:
                user.set_password("password123")
            user.save()
            users.append(user)

        # Employees
        for i in range(1, num_users + 1):
            username = f"emp{i:03d}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": "Emp",
                    "last_name": f"{i:03d}",
                    "role": UserRole.EMPLOYEE,
                    "is_active": True,
                },
            )
            if departments:
                user.department = departments[i % len(departments)]
            if not user.password:
                user.set_password("password123")
            user.save()
            users.append(user)

        return users

    def _seed_checkins(self, users: list[User], areas: list[Area], per_user: int):
        if not users or not areas:
            return

        now = timezone.now()
        for user in users:
            for n in range(per_user):
                area = random.choice(areas)
                # jitter around area center within ~100m
                lat = area.lat + random.uniform(-0.0005, 0.0005)
                lng = area.lng + random.uniform(-0.0005, 0.0005)
                ts = now - timedelta(
                    days=random.randint(0, 7), hours=random.randint(0, 8)
                )
                checkin = Checkin.objects.create(
                    user=user,
                    area=area,
                    lat=lat,
                    lng=lng,
                    note=f"Checkin demo #{n+1} của {user.username}",
                    ip="127.0.0.1",
                    user_agent="seed-script",
                )
                # optional distance if model supports it
                try:
                    from apps.checkin.utils import haversine_m  # type: ignore

                    checkin.distance_m = haversine_m(area.lat, area.lng, lat, lng)
                except Exception:
                    pass
                # set created_at if model allows
                try:
                    Checkin.objects.filter(id=checkin.id).update(created_at=ts)
                except Exception:
                    pass
