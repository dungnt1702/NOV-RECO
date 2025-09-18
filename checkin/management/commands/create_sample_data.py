from django.core.management.base import BaseCommand
from users.models import User
from checkin.models import Area, Location

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho areas và locations'

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu mẫu...')
        
        # Lấy admin user để tạo areas
        admin = User.objects.filter(role='admin').first()
        if not admin:
            self.stdout.write(self.style.ERROR('❌ Không tìm thấy admin user!'))
            return
        
        # Tạo Areas mẫu
        areas_data = [
            {
                'name': 'Văn phòng chính',
                'description': 'Tòa nhà văn phòng chính của công ty',
                'lat': 10.7769,
                'lng': 106.7009,
                'radius_m': 100,
            },
            {
                'name': 'Chi nhánh Quận 1',
                'description': 'Chi nhánh tại Quận 1, TP.HCM',
                'lat': 10.7769,
                'lng': 106.7009,
                'radius_m': 150,
            },
            {
                'name': 'Kho hàng Bình Dương',
                'description': 'Kho hàng tại Bình Dương',
                'lat': 10.9804,
                'lng': 106.6519,
                'radius_m': 200,
            },
        ]
        
        for area_data in areas_data:
            area, created = Area.objects.get_or_create(
                name=area_data['name'],
                defaults={
                    'description': area_data['description'],
                    'lat': area_data['lat'],
                    'lng': area_data['lng'],
                    'radius_m': area_data['radius_m'],
                    'created_by': admin,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Đã tạo Area: {area.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Area đã tồn tại: {area.name}')
                )
        
        # Tạo Locations mẫu (legacy)
        locations_data = [
            {
                'name': 'Trụ sở cũ',
                'lat': 10.7769,
                'lng': 106.7009,
                'radius_m': 50,
            },
            {
                'name': 'Văn phòng phụ',
                'lat': 10.7769,
                'lng': 106.7009,
                'radius_m': 80,
            },
        ]
        
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={
                    'lat': loc_data['lat'],
                    'lng': loc_data['lng'],
                    'radius_m': loc_data['radius_m'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Đã tạo Location: {location.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Location đã tồn tại: {location.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Hoàn thành tạo dữ liệu mẫu!')
        )
