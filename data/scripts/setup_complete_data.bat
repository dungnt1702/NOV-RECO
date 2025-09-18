@echo off
echo ================================================
echo        NOV-RECO COMPLETE DATA SETUP
echo ================================================
echo.

cd /d "%~dp0..\.."

echo [1/3] Setting up user groups and permissions...
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe manage.py setup_user_groups
echo.

echo [2/3] Creating sample users...
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe manage.py create_sample_users
echo.

echo [3/3] Creating sample areas...
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe manage.py create_sample_areas
echo.

echo ================================================
echo           SETUP COMPLETE!
echo ================================================
echo.
echo THÔNG TIN ĐĂNG NHẬP:
echo.
echo 🔴 Super Admin: superadmin / admin123
echo    - Toàn quyền hệ thống
echo.
echo 🟡 Quản lý: quanly / quanly123  
echo    - Xem và sửa toàn bộ
echo.
echo 🟢 Thư ký: thuky / thuky123
echo    - Xem và sửa toàn bộ (trừ user management)
echo.
echo 🔵 Nhân viên 1: nhanvien1 / nhanvien123
echo    - Xem và checkin
echo.
echo 🔵 Nhân viên 2: nhanvien2 / nhanvien123
echo    - Xem và checkin
echo.
echo ================================================
echo Access: http://reco.local
echo Admin:  http://reco.local/admin
echo ================================================
echo.
pause
