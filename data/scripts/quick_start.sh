#!/bin/bash

# NOV-RECO Check-in System - Quick Start Script
echo "🎯 NOV-RECO Check-in System - Quick Start"
echo "=========================================="

# Dừng server cũ nếu có
echo "🛑 Dừng server cũ..."
pkill -f "python3 manage.py runserver" 2>/dev/null || true
sleep 2

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy!"
    exit 1
fi

# Kiểm tra manage.py
if [ ! -f "manage.py" ]; then
    echo "❌ Không tìm thấy manage.py. Hãy chạy script trong thư mục dự án."
    exit 1
fi

# Cài đặt dependencies
echo "📦 Cài đặt dependencies..."
python3 -m pip install -r requirements.txt --quiet

# Chạy migrations
echo "🔄 Chạy migrations..."
python3 manage.py migrate --quiet

# Tạo admin nếu chưa có
echo "👤 Kiểm tra admin account..."
python3 manage.py shell -c "
from checkin.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('🔧 Tạo admin mặc định...')
    User.objects.create_superuser(
        username='admin@nov-reco.com',
        email='admin@nov-reco.com',
        password='admin123',
        first_name='Admin',
        last_name='NOV-RECO',
        role='admin',
        employee_id='ADMIN001'
    )
    print('✅ Admin: admin@nov-reco.com / admin123')
else:
    print('✅ Admin đã tồn tại')
" 2>/dev/null

# Khởi động server
echo "🚀 Khởi động server..."
echo "📍 URL: http://localhost:3000"
echo "🛑 Nhấn Ctrl+C để dừng"
echo "=========================================="

python3 manage.py runserver 127.0.0.1:3000
