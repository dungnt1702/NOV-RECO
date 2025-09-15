# Cấu hình server cho dự án Django
import os

# Cấu hình server
DEFAULT_PORT = 3000
DEFAULT_HOST = '0.0.0.0'

# Lấy port từ biến môi trường hoặc sử dụng default
def get_server_config():
    port = int(os.environ.get('SERVER_PORT', DEFAULT_PORT))
    host = os.environ.get('SERVER_HOST', DEFAULT_HOST)
    return host, port

# Cấu hình Django
DJANGO_SETTINGS = {
    'DEBUG': os.environ.get('DJANGO_DEBUG', '1') == '1',
    'SECRET_KEY': os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-me'),
    'SITE_ID': int(os.environ.get('SITE_ID', '1')),
}
