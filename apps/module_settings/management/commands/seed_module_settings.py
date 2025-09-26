from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.module_settings.models import ModuleSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Tạo default module settings cho hệ thống'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Xóa tất cả settings hiện tại và tạo lại',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Đang xóa tất cả module settings hiện tại...')
            ModuleSettings.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Đã xóa tất cả module settings')
            )

        # Lấy superuser đầu tiên làm created_by
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            self.stdout.write(
                self.style.ERROR('Không tìm thấy Super admin nào!')
            )
            return

        # Default module settings
        default_modules = [
            {
                'module_name': 'checkin',
                'display_name': 'Hệ thống Check-in',
                'description': 'Quản lý chấm công, check-in/check-out của nhân viên',
                'is_enabled': True,
            },
            {
                'module_name': 'location',
                'display_name': 'Quản lý Địa điểm',
                'description': 'Quản lý các địa điểm làm việc, văn phòng',
                'is_enabled': True,
            },
            {
                'module_name': 'users',
                'display_name': 'Quản lý Người dùng',
                'description': 'Quản lý nhân viên, phòng ban, văn phòng',
                'is_enabled': True,
            },
            {
                'module_name': 'dashboard',
                'display_name': 'Dashboard',
                'description': 'Trang tổng quan, thống kê hệ thống',
                'is_enabled': True,
            },
            {
                'module_name': 'notifications',
                'display_name': 'Thông báo',
                'description': 'Hệ thống thông báo cho người dùng',
                'is_enabled': True,
            },
            {
                'module_name': 'absence',
                'display_name': 'Quản lý Nghỉ phép',
                'description': 'Quản lý đơn xin nghỉ phép, phê duyệt',
                'is_enabled': True,
            },
            {
                'module_name': 'reports',
                'display_name': 'Báo cáo',
                'description': 'Tạo và xuất các báo cáo thống kê',
                'is_enabled': True,
            },
            {
                'module_name': 'analytics',
                'display_name': 'Phân tích',
                'description': 'Phân tích dữ liệu, biểu đồ thống kê',
                'is_enabled': True,
            },
            {
                'module_name': 'automation_test',
                'display_name': 'Kiểm thử Tự động',
                'description': 'Công cụ kiểm thử tự động cho hệ thống',
                'is_enabled': False,  # Tắt mặc định
            },
        ]

        created_count = 0
        updated_count = 0

        for module_data in default_modules:
            module_name = module_data['module_name']
            
            try:
                module, created = ModuleSettings.objects.get_or_create(
                    module_name=module_name,
                    defaults={
                        'display_name': module_data['display_name'],
                        'description': module_data['description'],
                        'is_enabled': module_data['is_enabled'],
                        'created_by': superuser,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Tạo module: {module.display_name}')
                    )
                else:
                    # Cập nhật thông tin nếu cần
                    updated = False
                    if module.display_name != module_data['display_name']:
                        module.display_name = module_data['display_name']
                        updated = True
                    if module.description != module_data['description']:
                        module.description = module_data['description']
                        updated = True
                    
                    if updated:
                        module.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Cập nhật module: {module.display_name}')
                        )
                    else:
                        self.stdout.write(
                            f'  Module đã tồn tại: {module.display_name}'
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Lỗi tạo module {module_name}: {str(e)}')
                )

        # Kết quả
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Tổng kết:')
        )
        self.stdout.write(f'  - Modules mới tạo: {created_count}')
        self.stdout.write(f'  - Modules cập nhật: {updated_count}')
        self.stdout.write(f'  - Tổng modules: {ModuleSettings.objects.count()}')
        
        # Hiển thị trạng thái
        enabled_count = ModuleSettings.objects.filter(is_enabled=True).count()
        disabled_count = ModuleSettings.objects.filter(is_enabled=False).count()
        
        self.stdout.write(f'  - Modules đang bật: {enabled_count}')
        self.stdout.write(f'  - Modules đang tắt: {disabled_count}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Hoàn tất tạo default module settings!')
        )
