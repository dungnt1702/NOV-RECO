@echo off

REM NOV-RECO Check-in System - Quick Start Script for Windows
echo 🎯 NOV-RECO Check-in System - Quick Start (Windows)
echo ======================================================

REM Di chuyển đến thư mục gốc của dự án
cd /d "%~dp0..\.."

REM Dừng server cũ nếu có
echo 🛑 Dừng server cũ...
taskkill /f /im python.exe 2>nul
taskkill /f /im python3.exe 2>nul
timeout /t 2 /nobreak >nul

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python không được tìm thấy!
    pause
    exit /b 1
)

REM Kiểm tra manage.py
if not exist "manage.py" (
    echo ❌ Không tìm thấy manage.py. Hãy chạy script trong thư mục dự án.
    pause
    exit /b 1
)

REM Cài đặt dependencies
echo 📦 Cài đặt dependencies...
python -m pip install -r requirements.txt --quiet --upgrade

REM Chạy migrations
echo 🔄 Chạy migrations...
python manage.py migrate

REM Thu thập static files
echo 📁 Thu thập static files...
python manage.py collectstatic --noinput

REM Kiểm tra admin account
echo 👤 Kiểm tra admin account...
python manage.py shell -c "
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
" 2>nul

REM Kiểm tra cấu hình
echo 🔍 Kiểm tra cấu hình...
python manage.py check

REM Khởi động server
echo 🚀 Khởi động server...
echo 📍 URL: http://localhost:3000
echo 🛑 Nhấn Ctrl+C để dừng
echo ======================================================
python manage.py runserver 127.0.0.1:3000
