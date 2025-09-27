#!/usr/bin/env python
import os
import sys

import django
from django.core.management import execute_from_command_line

from config import DEFAULT_PORT, get_server_config


def main():
    # Thiết lập Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    django.setup()

    # Lấy cấu hình server
    host, default_port = get_server_config()

    # Lấy port từ command line argument hoặc sử dụng default
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(
                f"Port không hợp lệ: {sys.argv[1]}. Sử dụng port mặc định: {default_port}"
            )
            port = default_port
    else:
        port = default_port

    # Chạy server
    print(f"🚀 Khởi động Django server trên {host}:{port}...")
    print(f"📱 Truy cập: http://localhost:{port}")
    print("⏹️  Nhấn Ctrl+C để dừng server")

    execute_from_command_line(["manage.py", "runserver", f"{host}:{port}"])


if __name__ == "__main__":
    main()
