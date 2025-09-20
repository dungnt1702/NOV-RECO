@echo off

REM NOV-RECO Script Manager for Windows
echo 🎯 NOV-RECO Script Manager
echo ==========================

REM Di chuyển đến thư mục gốc của dự án
cd /d "%~dp0..\.."

:menu
echo.
echo Chọn script để chạy:
echo 1^) Quick Start (Khởi động nhanh)
echo 2^) Setup Complete Data (Thiết lập dữ liệu đầy đủ)
echo 3^) Start Server Only (Chỉ khởi động server)
echo 4^) Start with Browser (Khởi động và mở browser)
echo 5^) Run Server (Python script)
echo 6^) Start Server (Advanced Python script)
echo 0^) Exit
echo.

set /p choice="Nhập lựa chọn (0-6): "

if "%choice%"=="1" (
    echo 🚀 Chạy Quick Start...
    call data\scripts\quick_start_windows.bat
    goto continue
)
if "%choice%"=="2" (
    echo 🔧 Chạy Setup Complete Data...
    call data\scripts\setup_complete_data.bat
    goto continue
)
if "%choice%"=="3" (
    echo 🖥️  Chạy Start Server Only...
    call data\scripts\start_server.sh
    goto continue
)
if "%choice%"=="4" (
    echo 🌐 Chạy Start with Browser...
    call data\scripts\start_reco_local.bat
    goto continue
)
if "%choice%"=="5" (
    echo 🐍 Chạy Run Server (Python)...
    python data\scripts\run_server.py
    goto continue
)
if "%choice%"=="6" (
    echo ⚡ Chạy Start Server (Advanced)...
    python data\scripts\start_server.py
    goto continue
)
if "%choice%"=="0" (
    echo 👋 Tạm biệt!
    exit /b 0
)

echo ❌ Lựa chọn không hợp lệ!

:continue
echo.
pause
goto menu
