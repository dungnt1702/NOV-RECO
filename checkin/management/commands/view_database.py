from django.core.management.base import BaseCommand
from users.models import User
from checkin.models import Checkin, Area, Location

class Command(BaseCommand):
    help = 'Xem dữ liệu trong database'

    def handle(self, *args, **options):
        self.stdout.write('📊 DỮ LIỆU TRONG DATABASE\n')
        
        # Users
        users = User.objects.all()
        self.stdout.write(f'👥 USERS ({users.count()}):')
        for user in users:
            self.stdout.write(f'  - {user.username} ({user.get_role_display()}) - {user.email}')
        self.stdout.write('')
        
        # Checkins
        checkins = Checkin.objects.all()
        self.stdout.write(f'📝 CHECKINS ({checkins.count()}):')
        for checkin in checkins[:10]:  # Chỉ hiển thị 10 checkin đầu
            self.stdout.write(f'  - {checkin.user.username} at {checkin.created_at.strftime("%d/%m/%Y %H:%M")}')
        if checkins.count() > 10:
            self.stdout.write(f'  ... và {checkins.count() - 10} checkin khác')
        self.stdout.write('')
        
        # Areas
        areas = Area.objects.all()
        self.stdout.write(f'🗺️ AREAS ({areas.count()}):')
        for area in areas:
            self.stdout.write(f'  - {area.name} ({area.lat}, {area.lng}) - R: {area.radius_m}m')
        self.stdout.write('')
        
        # Locations
        locations = Location.objects.all()
        self.stdout.write(f'📍 LOCATIONS ({locations.count()}):')
        for location in locations:
            self.stdout.write(f'  - {location.name} ({location.lat}, {location.lng}) - R: {location.radius_m}m')
        self.stdout.write('')
        
        self.stdout.write('✅ Hoàn thành xem dữ liệu!')
