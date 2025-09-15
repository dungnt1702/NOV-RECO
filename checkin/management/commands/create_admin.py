from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from checkin.models import UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo tài khoản admin'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email của admin')
        parser.add_argument('--password', type=str, help='Mật khẩu của admin')
        parser.add_argument('--first-name', type=str, help='Tên của admin')
        parser.add_argument('--last-name', type=str, help='Họ của admin')

    def handle(self, *args, **options):
        email = options.get('email') or 'admin@nov-reco.com'
        password = options.get('password') or 'admin123'
        first_name = options.get('first_name') or 'Admin'
        last_name = options.get('last_name') or 'NOV-RECO'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin với email {email} đã tồn tại!')
            )
            return

        admin = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
            employee_id='ADMIN001'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Đã tạo admin thành công!')
        )
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
