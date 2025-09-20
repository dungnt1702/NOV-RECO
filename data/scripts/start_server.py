#!/usr/bin/env python3
"""
Script tự động khởi động Django server
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def kill_existing_servers():
    """Dừng các server đang chạy trên port 3000"""
    try:
        # Tìm process đang chạy trên port 3000
        result = subprocess.run(['lsof', '-ti:3000'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"Đã dừng process {pid}")
                    except ProcessLookupError:
                        pass
        time.sleep(2)  # Đợi process dừng hoàn toàn
    except Exception as e:
        print(f"Lỗi khi dừng server: {e}")

def check_dependencies():
    """Kiểm tra và cài đặt dependencies"""
    print("🔍 Kiểm tra dependencies...")
    
    # Kiểm tra requirements.txt
    if not os.path.exists('requirements.txt'):
        print("❌ Không tìm thấy requirements.txt")
        return False
    
    # Cài đặt dependencies
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies đã được cài đặt")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt dependencies: {e}")
        return False

def run_migrations():
    """Chạy migrations"""
    print("🔄 Chạy migrations...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Migrations hoàn thành")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi migrations: {e}")
        return False

def create_superuser_if_needed():
    """Tạo superuser nếu chưa có"""
    print("👤 Kiểm tra superuser...")
    try:
        # Kiểm tra xem đã có superuser chưa
        result = subprocess.run([sys.executable, 'manage.py', 'shell', '-c', 
                               'from checkin.models import User; print(User.objects.filter(is_superuser=True).exists())'], 
                              capture_output=True, text=True)
        
        if 'True' not in result.stdout:
            print("🔧 Tạo superuser mặc định...")
            subprocess.run([sys.executable, 'manage.py', 'create_admin'], check=True)
            print("✅ Đã tạo admin: admin@nov-reco.com / admin123")
        else:
            print("✅ Superuser đã tồn tại")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi tạo superuser: {e}")
        return False

def start_server():
    """Khởi động Django server"""
    print("🚀 Khởi động Django server...")
    print("📍 Server sẽ chạy tại: http://localhost:3000")
    print("🛑 Nhấn Ctrl+C để dừng server")
    print("-" * 50)
    
    try:
        # Khởi động server
        subprocess.run([sys.executable, 'manage.py', 'runserver', '127.0.0.1:3000'])
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng server")
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {e}")

def main():
    """Hàm chính"""
    print("=" * 60)
    print("🎯 NOV-RECO Check-in System - Auto Startup")
    print("=" * 60)
    
    # Kiểm tra đang ở đúng thư mục
    if not os.path.exists('manage.py'):
        print("❌ Không tìm thấy manage.py. Hãy chạy script trong thư mục dự án.")
        return
    
    # Dừng server cũ
    kill_existing_servers()
    
    # Kiểm tra và cài đặt dependencies
    if not check_dependencies():
        return
    
    # Chạy migrations
    if not run_migrations():
        return
    
    # Tạo superuser nếu cần
    if not create_superuser_if_needed():
        return
    
    # Khởi động server
    start_server()

if __name__ == "__main__":
    main()
