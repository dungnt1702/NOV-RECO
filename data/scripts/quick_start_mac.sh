#!/bin/bash

# NOV-RECO Check-in System - Quick Start Script for macOS/Linux
echo "🎯 NOV-RECO Check-in System - Quick Start (macOS/Linux)"
echo "======================================================"

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Di chuyển đến thư mục gốc của dự án
cd "$(dirname "$0")/../.."

# Dừng server cũ nếu có
echo -e "${YELLOW}🛑 Dừng server cũ...${NC}"
pkill -f "python3 manage.py runserver" 2>/dev/null || true
pkill -f "python manage.py runserver" 2>/dev/null || true
sleep 2

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 không được tìm thấy!${NC}"
    exit 1
fi

# Kiểm tra manage.py
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Không tìm thấy manage.py. Hãy chạy script trong thư mục dự án.${NC}"
    exit 1
fi

# Cài đặt dependencies
echo -e "${BLUE}📦 Cài đặt dependencies...${NC}"
python3 -m pip install -r requirements.txt --quiet --upgrade

# Chạy migrations
echo -e "${BLUE}🔄 Chạy migrations...${NC}"
python3 manage.py migrate

# Thu thập static files
echo -e "${BLUE}📁 Thu thập static files...${NC}"
python3 manage.py collectstatic --noinput

# Kiểm tra admin account
echo -e "${BLUE}👤 Kiểm tra admin account...${NC}"
python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
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

# Kiểm tra cấu hình
echo -e "${BLUE}🔍 Kiểm tra cấu hình...${NC}"
python3 manage.py check

# Khởi động server
echo -e "${GREEN}🚀 Khởi động server...${NC}"
echo -e "${GREEN}📍 URL: http://localhost:3000${NC}"
echo -e "${YELLOW}🛑 Nhấn Ctrl+C để dừng${NC}"
echo -e "${GREEN}======================================================"
python3 manage.py runserver 127.0.0.1:3000
