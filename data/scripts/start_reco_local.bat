@echo off
echo Starting NOV-RECO Check-in System...
echo.

REM Khởi động Django development server
echo Starting Django server on port 3000...
start "Django Server" cmd /k "cd /d \"%~dp0..\..\" && C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe manage.py runserver 3000"

REM Đợi một chút để server khởi động
timeout /t 3 /nobreak >nul

REM Mở browser với reco.local
echo Opening browser at http://reco.local...
start http://reco.local

echo.
echo NOV-RECO is now running at:
echo - Local: http://reco.local
echo - Admin: http://reco.local/admin
echo - Username: admin
echo - Password: admin123
echo.
echo Press any key to exit...
pause >nul
