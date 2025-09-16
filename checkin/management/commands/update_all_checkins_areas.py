from django.core.management.base import BaseCommand
from checkin.models import Checkin, Area, Location
from checkin.utils import haversine_m


class Command(BaseCommand):
    help = "Cập nhật tất cả check-in dựa trên các area hiện có"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ hiển thị kết quả mà không cập nhật database",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Cập nhật cả check-in đã có area",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - Không cập nhật database")
            )

        # Lấy tất cả check-in
        if force:
            checkins = Checkin.objects.all()
            self.stdout.write(
                "Cập nhật TẤT CẢ check-in (bao gồm cả đã có area)"
            )
        else:
            checkins = Checkin.objects.filter(area__isnull=True)
            self.stdout.write("Chỉ cập nhật check-in chưa có area")

        self.stdout.write(f"Tìm thấy {checkins.count()} check-in cần xử lý")

        updated_count = 0
        areas = Area.objects.filter(is_active=True)

        if not areas.exists():
            self.stdout.write(
                self.style.WARNING("Không có area nào được định nghĩa!")
            )
            return

        self.stdout.write(f"Có {areas.count()} area đang hoạt động")

        for checkin in checkins:
            lat = checkin.lat
            lng = checkin.lng

            # Tìm area phù hợp nhất
            valid_areas = []
            for area in areas:
                if area.contains_point(lat, lng):
                    dist = haversine_m(lat, lng, area.lat, area.lng)
                    valid_areas.append((area, dist))

            if valid_areas:
                # Chọn area gần nhất
                closest_area, closest_distance = min(
                    valid_areas, key=lambda x: x[1]
                )

                # Chỉ cập nhật nếu chưa có area hoặc area mới gần hơn
                should_update = (
                    not checkin.area
                    or checkin.area != closest_area
                    or closest_distance < (checkin.distance_m or float("inf"))
                )

                if should_update:
                    if not dry_run:
                        checkin.area = closest_area
                        checkin.distance_m = closest_distance
                        checkin.save()

                    self.stdout.write(
                        f"Check-in {checkin.id}: {lat:.6f}, {lng:.6f} -> "
                        f'Area "{closest_area.name}" (khoảng cách: {closest_distance:.1f}m)'
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        f"Check-in {checkin.id}: Đã có area phù hợp - {checkin.area.name}"
                    )
            else:
                # Không tìm thấy area phù hợp, tìm location
                locations = Location.objects.filter(is_active=True)
                valid_locations = []

                for loc in locations:
                    dist = haversine_m(lat, lng, loc.lat, loc.lng)
                    if dist <= loc.radius_m:
                        valid_locations.append((loc, dist))

                if valid_locations:
                    closest_location, closest_distance = min(
                        valid_locations, key=lambda x: x[1]
                    )

                    # Chỉ cập nhật nếu chưa có location hoặc location mới gần hơn
                    should_update = (
                        not checkin.location
                        or checkin.location != closest_location
                        or closest_distance
                        < (checkin.distance_m or float("inf"))
                    )

                    if should_update:
                        if not dry_run:
                            checkin.area = None
                            checkin.location = closest_location
                            checkin.distance_m = closest_distance
                            checkin.save()

                        self.stdout.write(
                            f"Check-in {checkin.id}: {lat:.6f}, {lng:.6f} -> "
                            f'Location "{closest_location.name}" (khoảng cách: {closest_distance:.1f}m)'
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            f"Check-in {checkin.id}: Đã có location phù hợp - {checkin.location.name}"
                        )
                else:
                    self.stdout.write(
                        f"Check-in {checkin.id}: {lat:.6f}, {lng:.6f} -> "
                        f"Không tìm thấy area/location phù hợp"
                    )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN: Sẽ cập nhật {updated_count} check-in"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Đã cập nhật {updated_count} check-in")
            )
