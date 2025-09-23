from django.core.management.base import BaseCommand
from apps.checkin.models import Checkin
from apps.checkin.utils import find_nearest_area


class Command(BaseCommand):
    help = 'Cập nhật khu vực cho tất cả check-in dựa trên tọa độ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Chỉ hiển thị kết quả mà không cập nhật database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Đang cập nhật khu vực cho các check-in...')
        
        checkins = Checkin.objects.all()
        updated_count = 0
        not_found_count = 0
        
        for checkin in checkins:
            # Tìm khu vực gần nhất dựa trên tọa độ
            area, distance = find_nearest_area(checkin.lat, checkin.lng)
            
            if area:
                if not dry_run:
                    checkin.area = area
                    checkin.distance_m = distance
                    checkin.save()
                
                updated_count += 1
                self.stdout.write(
                    f'Check-in {checkin.id}: {checkin.area.name if checkin.area else "Không có"} -> {area.name} '
                    f'(khoảng cách: {distance:.2f}m)'
                )
            else:
                not_found_count += 1
                self.stdout.write(
                    f'Check-in {checkin.id}: Không tìm thấy khu vực phù hợp'
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDRY RUN - Không có thay đổi nào được lưu\n'
                    f'Tổng cộng: {checkins.count()} check-in\n'
                    f'Sẽ cập nhật: {updated_count}\n'
                    f'Không tìm thấy khu vực: {not_found_count}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nHoàn thành!\n'
                    f'Tổng cộng: {checkins.count()} check-in\n'
                    f'Đã cập nhật: {updated_count}\n'
                    f'Không tìm thấy khu vực: {not_found_count}'
                )
            )
