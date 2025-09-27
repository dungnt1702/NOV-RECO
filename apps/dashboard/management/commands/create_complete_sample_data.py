#!/usr/bin/env python
"""
Management command để tạo dữ liệu mẫu đầy đủ cho tất cả các module
"""
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from apps.users.models import User, UserRole, Office, Department
from apps.location.models import Location
from apps.checkin.models import Checkin, Checkout, CheckinType
from apps.absence.models import AbsenceType, AbsenceRequest, ApprovalWorkflow, ApprovalHistory
from apps.notifications.models import Notification
from apps.module_settings.models import ModuleSettings
from apps.automation_test.models import TestSession, TestResult, TestLog

User = get_user_model()


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu đầy đủ cho tất cả các module"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xóa dữ liệu cũ trước khi tạo mới",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("🗑️  Xóa dữ liệu cũ...")
            self.clear_data()

        self.stdout.write("🚀 Bắt đầu tạo dữ liệu mẫu...")

        with transaction.atomic():
            # 1. Tạo Module Settings
            self.create_module_settings()

            # 2. Tạo Offices và Departments
            offices, departments = self.create_offices_and_departments()

            # 3. Tạo Users
            users = self.create_users(offices, departments)

            # 4. Tạo Locations
            locations = self.create_locations(users)

            # 5. Tạo Absence Types và Workflows
            absence_types, workflows = self.create_absence_types_and_workflows(departments)

            # 6. Tạo Check-ins và Check-outs
            self.create_checkins_and_checkouts(users, locations)

            # 7. Tạo Absence Requests
            self.create_absence_requests(users, absence_types, workflows)

            # 8. Tạo Notifications
            self.create_notifications(users)

            # 9. Tạo Test Sessions
            self.create_test_sessions(users)

        self.stdout.write(
            self.style.SUCCESS("✅ Hoàn thành tạo dữ liệu mẫu!")
        )
        self.print_login_info(users)

    def clear_data(self):
        """Xóa dữ liệu cũ"""
        models_to_clear = [
            TestLog, TestResult, TestSession,
            ApprovalHistory, AbsenceRequest, ApprovalWorkflow, AbsenceType,
            Notification, Checkout, Checkin, Location,
            Department, Office, ModuleSettings
        ]
        
        # Giữ lại superuser
        User.objects.filter(is_superuser=False).delete()
        
        for model in models_to_clear:
            model.objects.all().delete()

    def create_module_settings(self):
        """Tạo cài đặt module"""
        self.stdout.write("⚙️  Tạo Module Settings...")
        
        modules = [
            ("checkin", "Hệ thống Check-in", "Quản lý chấm công và điểm danh"),
            ("location", "Quản lý Địa điểm", "Quản lý các địa điểm làm việc"),
            ("users", "Quản lý Người dùng", "Quản lý thông tin nhân viên"),
            ("dashboard", "Dashboard", "Bảng điều khiển tổng quan"),
            ("notifications", "Thông báo", "Hệ thống thông báo"),
            ("absence", "Quản lý Vắng mặt", "Quản lý đơn xin nghỉ phép"),
            ("reports", "Báo cáo", "Hệ thống báo cáo"),
            ("analytics", "Phân tích", "Phân tích dữ liệu"),
            ("automation_test", "Kiểm thử tự động", "Hệ thống kiểm thử"),
        ]
        
        for module_name, display_name, description in modules:
            ModuleSettings.objects.get_or_create(
                module_name=module_name,
                defaults={
                    "display_name": display_name,
                    "description": description,
                    "is_enabled": True,
                }
            )

    def create_offices_and_departments(self):
        """Tạo văn phòng và phòng ban"""
        self.stdout.write("🏢 Tạo Offices và Departments...")
        
        # Tạo Offices
        offices_data = [
            ("Văn phòng Hà Nội", "Trụ sở chính tại Hà Nội"),
            ("Văn phòng TP.HCM", "Chi nhánh tại TP. Hồ Chí Minh"),
            ("Văn phòng Đà Nẵng", "Chi nhánh tại Đà Nẵng"),
        ]
        
        offices = []
        for name, description in offices_data:
            office, created = Office.objects.get_or_create(
                name=name,
                defaults={"description": description}
            )
            offices.append(office)
            if created:
                self.stdout.write(f"  ✅ Tạo office: {name}")

        # Tạo Departments
        departments_data = [
            ("IT", "Công nghệ thông tin"),
            ("HR", "Nhân sự"),
            ("Finance", "Tài chính"),
            ("Sales", "Kinh doanh"),
            ("Marketing", "Tiếp thị"),
            ("Operations", "Vận hành"),
        ]
        
        departments = []
        for name, description in departments_data:
            for office in offices:
                dept, created = Department.objects.get_or_create(
                    name=name,
                    office=office,
                    defaults={"description": description}
                )
                departments.append(dept)
                if created:
                    self.stdout.write(f"  ✅ Tạo department: {name} - {office.name}")

        return offices, departments

    def create_users(self, offices, departments):
        """Tạo users"""
        self.stdout.write("👥 Tạo Users...")
        
        users_data = [
            # Admin
            ("admin", "admin@nov-reco.com", "Admin", "System", UserRole.ADMIN, "ADM001", None),
            
            # Managers
            ("manager_it", "manager.it@nov-reco.com", "Nguyễn", "Văn A", UserRole.MANAGER, "MGR001", "IT"),
            ("manager_hr", "manager.hr@nov-reco.com", "Trần", "Thị B", UserRole.MANAGER, "MGR002", "HR"),
            ("manager_sales", "manager.sales@nov-reco.com", "Lê", "Văn C", UserRole.MANAGER, "MGR003", "Sales"),
            
            # HCNS
            ("hcns_main", "hcns.main@nov-reco.com", "Phạm", "Thị D", UserRole.HCNS, "HCNS001", "HR"),
            ("hcns_recruit", "hcns.recruit@nov-reco.com", "Hoàng", "Văn E", UserRole.HCNS, "HCNS002", "HR"),
            
            # Employees
            ("dev_001", "dev.001@nov-reco.com", "Vũ", "Văn F", UserRole.EMPLOYEE, "EMP001", "IT"),
            ("dev_002", "dev.002@nov-reco.com", "Đặng", "Thị G", UserRole.EMPLOYEE, "EMP002", "IT"),
            ("dev_003", "dev.003@nov-reco.com", "Bùi", "Văn H", UserRole.EMPLOYEE, "EMP003", "IT"),
            ("accountant_001", "accountant.001@nov-reco.com", "Ngô", "Thị I", UserRole.EMPLOYEE, "EMP004", "Finance"),
            ("accountant_002", "accountant.002@nov-reco.com", "Dương", "Văn J", UserRole.EMPLOYEE, "EMP005", "Finance"),
            ("sales_001", "sales.001@nov-reco.com", "Lý", "Thị K", UserRole.EMPLOYEE, "EMP006", "Sales"),
            ("sales_002", "sales.002@nov-reco.com", "Võ", "Văn L", UserRole.EMPLOYEE, "EMP007", "Sales"),
            ("marketing_001", "marketing.001@nov-reco.com", "Đỗ", "Thị M", UserRole.EMPLOYEE, "EMP008", "Marketing"),
            ("ops_001", "ops.001@nov-reco.com", "Tạ", "Văn N", UserRole.EMPLOYEE, "EMP009", "Operations"),
        ]
        
        users = []
        for username, email, first_name, last_name, role, employee_id, dept_name in users_data:
            # Tìm department phù hợp
            department = None
            if dept_name:
                department = next((d for d in departments if d.name == dept_name), None)
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                    "employee_id": employee_id,
                    "department": department,
                    "phone": f"090{random.randint(1000000, 9999999)}",
                    "address": f"{random.randint(1, 999)} Đường {random.choice(['Nguyễn Huệ', 'Lê Lợi', 'Trần Hưng Đạo', 'Hai Bà Trưng'])}",
                    "position": self.get_position_for_role(role, dept_name),
                    "hire_date": date.today() - timedelta(days=random.randint(30, 1000)),
                    "is_active_employee": True,
                }
            )
            
            if created:
                user.set_password("password123")
                user.save()
                users.append(user)
                self.stdout.write(f"  ✅ Tạo user: {username} ({role})")
            else:
                users.append(user)

        return users

    def get_position_for_role(self, role, dept_name):
        """Lấy chức vụ phù hợp với role và department"""
        positions = {
            UserRole.ADMIN: "Giám đốc điều hành",
            UserRole.MANAGER: {
                "IT": "Trưởng phòng IT",
                "HR": "Trưởng phòng Nhân sự",
                "Sales": "Trưởng phòng Kinh doanh",
                "Finance": "Trưởng phòng Tài chính",
                "Marketing": "Trưởng phòng Marketing",
                "Operations": "Trưởng phòng Vận hành",
            },
            UserRole.HCNS: {
                "HR": "Chuyên viên Nhân sự",
            },
            UserRole.EMPLOYEE: {
                "IT": "Lập trình viên",
                "HR": "Chuyên viên Nhân sự",
                "Finance": "Kế toán viên",
                "Sales": "Nhân viên Kinh doanh",
                "Marketing": "Chuyên viên Marketing",
                "Operations": "Nhân viên Vận hành",
            }
        }
        
        if role == UserRole.ADMIN:
            return positions[role]
        elif role in [UserRole.MANAGER, UserRole.HCNS, UserRole.EMPLOYEE]:
            return positions[role].get(dept_name, "Nhân viên")
        return "Nhân viên"

    def create_locations(self, users):
        """Tạo locations"""
        self.stdout.write("📍 Tạo Locations...")
        
        locations_data = [
            ("Văn phòng chính Hà Nội", "Tòa nhà NOV-RECO, 123 Nguyễn Huệ, Hoàn Kiếm, Hà Nội", 21.0285, 105.8542, 100),
            ("Chi nhánh TP.HCM", "Tòa nhà Landmark, 456 Nguyễn Huệ, Quận 1, TP.HCM", 10.7769, 106.7009, 150),
            ("Chi nhánh Đà Nẵng", "Tòa nhà FPT, 789 Lê Duẩn, Hải Châu, Đà Nẵng", 16.0544, 108.2022, 120),
            ("Kho Bình Dương", "Khu công nghiệp VSIP, Thuận An, Bình Dương", 10.9804, 106.6519, 200),
            ("Văn phòng Quận 7", "Tòa nhà Saigon Trade Center, Quận 7, TP.HCM", 10.7308, 106.7194, 80),
        ]
        
        locations = []
        admin_user = next((u for u in users if u.role == UserRole.ADMIN), users[0])
        
        for name, address, lat, lng, radius in locations_data:
            location, created = Location.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"Địa điểm {name}",
                    "address": address,
                    "lat": lat,
                    "lng": lng,
                    "radius_m": radius,
                    "is_active": True,
                    "created_by": admin_user,
                }
            )
            locations.append(location)
            if created:
                self.stdout.write(f"  ✅ Tạo location: {name}")

        return locations

    def create_absence_types_and_workflows(self, departments):
        """Tạo absence types và workflows"""
        self.stdout.write("📋 Tạo Absence Types và Workflows...")
        
        # Tạo Absence Types
        absence_types_data = [
            ("Nghỉ phép năm", "ANNUAL", "Nghỉ phép năm theo quy định", True, 12, "#10B981"),
            ("Nghỉ ốm", "SICK", "Nghỉ ốm có giấy bác sĩ", True, None, "#F59E0B"),
            ("Nghỉ việc riêng", "PERSONAL", "Nghỉ việc riêng không lương", True, 5, "#3B82F6"),
            ("Nghỉ thai sản", "MATERNITY", "Nghỉ thai sản theo quy định", True, 180, "#EC4899"),
            ("Nghỉ không lương", "UNPAID", "Nghỉ không lương", True, None, "#6B7280"),
        ]
        
        absence_types = []
        for name, code, description, requires_approval, max_days, color in absence_types_data:
            absence_type, created = AbsenceType.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "requires_approval": requires_approval,
                    "max_days_per_year": max_days,
                    "color": color,
                    "is_active": True,
                }
            )
            absence_types.append(absence_type)
            if created:
                self.stdout.write(f"  ✅ Tạo absence type: {name}")

        # Tạo Approval Workflows
        workflows = []
        for department in departments:
            for absence_type in absence_types:
                workflow, created = ApprovalWorkflow.objects.get_or_create(
                    department=department,
                    absence_type=absence_type,
                    defaults={
                        "requires_department_manager": True,
                        "requires_department_deputy": False,
                        "requires_office_director": absence_type.code in ["MATERNITY", "UNPAID"],
                        "requires_office_deputy": False,
                        "requires_hr_approval": True,
                        "department_manager_priority": 1,
                        "department_deputy_priority": 2,
                        "office_director_priority": 3,
                        "office_deputy_priority": 4,
                        "department_manager_timeout_hours": 24,
                        "department_deputy_timeout_hours": 24,
                        "office_director_timeout_hours": 48,
                        "office_deputy_timeout_hours": 48,
                        "hr_timeout_hours": 24,
                        "is_active": True,
                    }
                )
                workflows.append(workflow)
                if created:
                    self.stdout.write(f"  ✅ Tạo workflow: {department.name} - {absence_type.name}")

        return absence_types, workflows

    def create_checkins_and_checkouts(self, users, locations):
        """Tạo check-ins và check-outs"""
        self.stdout.write("⏰ Tạo Check-ins và Check-outs...")
        
        # Tạo check-ins cho 30 ngày gần đây
        base_date = timezone.now() - timedelta(days=30)
        checkin_count = 0
        checkout_count = 0
        
        for day in range(30):
            current_date = base_date + timedelta(days=day)
            
            # Bỏ qua cuối tuần
            if current_date.weekday() >= 5:
                continue
                
            for user in users:
                if user.role == UserRole.ADMIN:
                    continue
                    
                # 80% chance có check-in
                if random.random() < 0.8:
                    location = random.choice(locations)
                    
                    # Tạo check-in
                    checkin_time = current_date.replace(
                        hour=random.randint(7, 9),
                        minute=random.randint(0, 59),
                        second=0,
                        microsecond=0
                    )
                    
                    # Thêm noise cho tọa độ
                    lat = location.lat + random.uniform(-0.001, 0.001)
                    lng = location.lng + random.uniform(-0.001, 0.001)
                    
                    checkin = Checkin.objects.create(
                        user=user,
                        location=location,
                        lat=lat,
                        lng=lng,
                        address=location.address,
                        note=random.choice(["", "Check-in sáng", "Đi làm đúng giờ", ""]),
                        checkin_type=random.choice([CheckinType.WORK, CheckinType.VISITOR]),
                        distance_m=random.uniform(10, 50),
                        ip=f"192.168.1.{random.randint(1, 254)}",
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                        created_at=checkin_time
                    )
                    checkin_count += 1
                    
                    # 70% chance có check-out
                    if random.random() < 0.7:
                        checkout_time = checkin_time + timedelta(
                            hours=random.randint(8, 10),
                            minutes=random.randint(0, 59)
                        )
                        
                        Checkout.objects.create(
                            user=user,
                            checkin=checkin,
                            lat=lat + random.uniform(-0.001, 0.001),
                            lng=lng + random.uniform(-0.001, 0.001),
                            address=location.address,
                            note=random.choice(["", "Check-out chiều", "Hoàn thành công việc", ""]),
                            distance_m=random.uniform(10, 50),
                            ip=f"192.168.1.{random.randint(1, 254)}",
                            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                            created_at=checkout_time
                        )
                        checkout_count += 1

        self.stdout.write(f"  ✅ Tạo {checkin_count} check-ins và {checkout_count} check-outs")

    def create_absence_requests(self, users, absence_types, workflows):
        """Tạo absence requests"""
        self.stdout.write("📝 Tạo Absence Requests...")
        
        absence_count = 0
        for user in users:
            if user.role == UserRole.ADMIN:
                continue
                
            # 30% chance có đơn xin nghỉ
            if random.random() < 0.3:
                absence_type = random.choice(absence_types)
                workflow = next((w for w in workflows if w.department == user.department and w.absence_type == absence_type), None)
                
                if workflow:
                    start_date = date.today() + timedelta(days=random.randint(1, 30))
                    end_date = start_date + timedelta(days=random.randint(1, 5))
                    
                    absence_request = AbsenceRequest.objects.create(
                        user=user,
                        absence_type=absence_type,
                        workflow=workflow,
                        start_date=start_date,
                        end_date=end_date,
                        total_days=Decimal(str((end_date - start_date).days + 1)),
                        reason=random.choice([
                            "Nghỉ phép năm",
                            "Có việc gia đình",
                            "Đi du lịch",
                            "Nghỉ ốm",
                            "Việc riêng",
                        ]),
                        status=random.choice(["pending", "approved", "rejected"]),
                        current_approver=user.department.manager if user.department and user.department.manager else None,
                        approval_level="department_manager",
                    )
                    absence_count += 1
                    
                    # Tạo approval history nếu đã được xử lý
                    if absence_request.status in ["approved", "rejected"]:
                        ApprovalHistory.objects.create(
                            absence_request=absence_request,
                            approver=absence_request.current_approver or user,
                            action="approved" if absence_request.status == "approved" else "rejected",
                            level="department_manager",
                            comment=random.choice([
                                "Đồng ý",
                                "Không đồng ý",
                                "Cần xem xét thêm",
                            ])
                        )

        self.stdout.write(f"  ✅ Tạo {absence_count} absence requests")

    def create_notifications(self, users):
        """Tạo notifications"""
        self.stdout.write("🔔 Tạo Notifications...")
        
        notification_count = 0
        for user in users:
            # Tạo 2-5 notifications cho mỗi user
            for _ in range(random.randint(2, 5)):
                notification = Notification.objects.create(
                    user=user,
                    title=random.choice([
                        "Thông báo check-in",
                        "Đơn xin nghỉ cần phê duyệt",
                        "Thông báo hệ thống",
                        "Nhắc nhở công việc",
                        "Cập nhật thông tin",
                    ]),
                    message=random.choice([
                        "Bạn có đơn xin nghỉ cần phê duyệt",
                        "Hệ thống sẽ bảo trì vào cuối tuần",
                        "Vui lòng cập nhật thông tin cá nhân",
                        "Có check-in bất thường cần xem xét",
                        "Thông báo mới từ quản lý",
                    ]),
                    type=random.choice([
                        "approval_required",
                        "system",
                        "checkin",
                        "absence",
                        "reminder",
                    ]),
                    is_read=random.choice([True, False]),
                    is_important=random.random() < 0.2,
                )
                notification_count += 1

        self.stdout.write(f"  ✅ Tạo {notification_count} notifications")

    def create_test_sessions(self, users):
        """Tạo test sessions"""
        self.stdout.write("🧪 Tạo Test Sessions...")
        
        test_count = 0
        for user in users[:3]:  # Chỉ tạo cho 3 user đầu
            for _ in range(random.randint(1, 3)):
                session = TestSession.objects.create(
                    session_id=f"TEST_{user.username}_{random.randint(1000, 9999)}",
                    user=user,
                    status=random.choice(["completed", "failed", "running"]),
                    total_tests=random.randint(10, 50),
                    passed_tests=random.randint(5, 45),
                    failed_tests=random.randint(0, 5),
                    skipped_tests=random.randint(0, 3),
                    duration=random.uniform(30, 300),
                    notes=random.choice([
                        "Test chức năng check-in",
                        "Test hệ thống thông báo",
                        "Test quản lý người dùng",
                    ])
                )
                test_count += 1
                
                # Tạo test results
                for i in range(session.total_tests):
                    TestResult.objects.create(
                        session=session,
                        test_name=f"test_{i+1}",
                        module=random.choice(["checkin", "users", "notifications", "absence"]),
                        status=random.choice(["passed", "failed", "skipped"]),
                        duration=random.uniform(0.1, 5.0),
                        error_message="" if random.random() < 0.8 else "Test failed due to timeout",
                    )

        self.stdout.write(f"  ✅ Tạo {test_count} test sessions")

    def print_login_info(self, users):
        """In thông tin đăng nhập"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 THÔNG TIN ĐĂNG NHẬP"))
        self.stdout.write("="*60)
        
        # Group users by role
        users_by_role = {}
        for user in users:
            if user.role not in users_by_role:
                users_by_role[user.role] = []
            users_by_role[user.role].append(user)
        
        for role, role_users in users_by_role.items():
            role_display = dict(UserRole.choices)[role]
            self.stdout.write(f"\n{role_display}:")
            for user in role_users[:3]:  # Chỉ hiển thị 3 user đầu
                self.stdout.write(f"  👤 {user.username} / password123")
                if user.department:
                    self.stdout.write(f"     Phòng ban: {user.department.name}")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🔑 Mật khẩu mặc định: password123")
        self.stdout.write("="*60)
