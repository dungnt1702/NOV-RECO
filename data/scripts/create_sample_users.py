#!/usr/bin/env python
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from checkin.models import User, UserRole

# Tạo Manager
manager = User.objects.create_user(
    username="manager@nov-reco.com",
    email="manager@nov-reco.com",
    password="manager123",
    first_name="Nguyễn",
    last_name="Quản Lý",
    role=UserRole.MANAGER,
    phone="0901234567",
    department="Quản lý",
    employee_id="MGR001",
)

# Tạo Employee 1
employee1 = User.objects.create_user(
    username="employee1@nov-reco.com",
    email="employee1@nov-reco.com",
    password="emp123",
    first_name="Trần",
    last_name="Nhân Viên",
    role=UserRole.EMPLOYEE,
    phone="0901234568",
    department="Kỹ thuật",
    employee_id="EMP001",
)

# Tạo Employee 2
employee2 = User.objects.create_user(
    username="employee2@nov-reco.com",
    email="employee2@nov-reco.com",
    password="emp123",
    first_name="Lê",
    last_name="Công Nhân",
    role=UserRole.EMPLOYEE,
    phone="0901234569",
    department="Kinh doanh",
    employee_id="EMP002",
)

print("✅ Đã tạo users mẫu thành công!")
print(f"👑 Admin: admin@nov-reco.com / admin123")
print(f"👨‍💼 Manager: manager@nov-reco.com / manager123")
print(f"👤 Employee 1: employee1@nov-reco.com / emp123")
print(f"👤 Employee 2: employee2@nov-reco.com / emp123")
