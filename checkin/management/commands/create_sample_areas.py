from django.core.management.base import BaseCommand
from users.models import User
from checkin.models import Area


class Command(BaseCommand):
    help = 'Create sample areas for testing'

    def handle(self, *args, **options):
        # Lấy user admin để làm created_by
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(username='superadmin').first()
            
            if not admin_user:
                self.stdout.write(
                    self.style.ERROR('No admin user found. Please create admin user first.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error finding admin user: {str(e)}')
            )
            return

        # Dữ liệu areas mẫu (Tọa độ Hà Nội và TP.HCM)
        sample_areas = [
            {
                'name': 'Văn phòng Hà Nội',
                'description': 'Trụ sở chính tại Hà Nội',
                'lat': 21.0285,
                'lng': 105.8542,
                'radius_m': 200,
            },
            {
                'name': 'Chi nhánh TP.HCM',
                'description': 'Chi nhánh tại Thành phố Hồ Chí Minh',
                'lat': 10.8231,
                'lng': 106.6297,
                'radius_m': 150,
            },
            {
                'name': 'Nhà máy Bắc Ninh',
                'description': 'Nhà máy sản xuất tại Bắc Ninh',
                'lat': 21.1861,
                'lng': 106.0763,
                'radius_m': 300,
            },
            {
                'name': 'Kho hàng Đồng Nai',
                'description': 'Kho bãi tại Đồng Nai',
                'lat': 10.9472,
                'lng': 107.0946,
                'radius_m': 250,
            },
            {
                'name': 'Showroom Đà Nẵng',
                'description': 'Showroom trưng bày tại Đà Nẵng',
                'lat': 16.0544,
                'lng': 108.2022,
                'radius_m': 100,
            },
        ]

        for area_data in sample_areas:
            # Kiểm tra area đã tồn tại chưa
            if Area.objects.filter(name=area_data['name']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Area {area_data["name"]} already exists')
                )
                continue
            
            # Tạo area mới
            try:
                area = Area.objects.create(
                    name=area_data['name'],
                    description=area_data['description'],
                    lat=area_data['lat'],
                    lng=area_data['lng'],
                    radius_m=area_data['radius_m'],
                    created_by=admin_user,
                    is_active=True,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created area: {area.name} ({area.radius_m}m radius)'
                    )
                )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating area {area_data["name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample areas created successfully!')
        )
