from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Quản trị viên"
    MANAGER = "manager", "Quản lý"
    HCNS = "hcns", "Nhân sự"
    EMPLOYEE = "employee", "Nhân viên"


class Office(models.Model):
    """Văn phòng"""

    name = models.CharField(max_length=100, unique=True, help_text="Tên văn phòng")
    description = models.TextField(blank=True, help_text="Mô tả văn phòng")

    # Địa điểm
    location = models.ForeignKey(
        "location.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Địa điểm của văn phòng",
    )

    # Quản lý cấp cao
    director = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="directed_offices",
        help_text="Giám đốc Văn phòng",
        limit_choices_to={"role__in": ["admin", "manager"]},
    )
    deputy_director = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deputy_directed_offices",
        help_text="Phó Giám đốc Văn phòng",
        limit_choices_to={"role__in": ["admin", "manager"]},
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Văn phòng"
        verbose_name_plural = "Văn phòng"

    def __str__(self):
        return self.name


class Department(models.Model):
    """Phòng ban"""

    name = models.CharField(max_length=100, help_text="Tên phòng ban")
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        null=True,  # Tạm thời cho phép null để migration
        help_text="Văn phòng",
    )
    description = models.TextField(blank=True, help_text="Mô tả phòng ban")

    # Quản lý phòng ban
    manager = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
        help_text="Trưởng phòng",
        limit_choices_to={"role__in": ["admin", "manager"]},
    )
    deputy_manager = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deputy_managed_departments",
        help_text="Phó phòng",
        limit_choices_to={"role__in": ["admin", "manager"]},
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["office__name", "name"]
        verbose_name = "Phòng ban"
        verbose_name_plural = "Phòng ban"
        unique_together = [
            "name",
            "office",
        ]  # Tên phòng ban chỉ unique trong cùng văn phòng

    def __str__(self):
        return f"{self.name} - {self.office.name}"

    @property
    def full_name(self):
        """Tên đầy đủ: Phòng ban - Văn phòng"""
        return f"{self.name} - {self.office.name}"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        help_text="Vai trò người dùng",
    )

    employee_id = models.CharField(
        max_length=20, unique=True, blank=True, null=True, help_text="Mã nhân viên"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Phòng ban",
    )
    phone = models.CharField(max_length=20, blank=True, help_text="Số điện thoại")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, help_text="Ảnh đại diện"
    )
    date_of_birth = models.DateField(null=True, blank=True, help_text="Ngày sinh")
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Nam"),
            ("female", "Nữ"),
            ("other", "Khác"),
        ],
        blank=True,
        help_text="Giới tính",
    )
    address = models.TextField(blank=True, help_text="Địa chỉ")
    emergency_contact = models.CharField(
        max_length=100, blank=True, help_text="Người liên hệ khẩn cấp"
    )
    emergency_phone = models.CharField(
        max_length=20, blank=True, help_text="Số điện thoại liên hệ khẩn cấp"
    )
    position = models.CharField(max_length=100, blank=True, help_text="Chức vụ")
    hire_date = models.DateField(null=True, blank=True, help_text="Ngày vào làm")
    salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, help_text="Lương"
    )
    work_schedule = models.CharField(
        max_length=100, blank=True, help_text="Lịch làm việc"
    )
    skills = models.TextField(blank=True, help_text="Kỹ năng")
    notes = models.TextField(blank=True, help_text="Ghi chú")
    is_active_employee = models.BooleanField(
        default=True, help_text="Nhân viên đang hoạt động"
    )

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        permissions = [
            # User management permissions
            ("can_manage_users", "Can manage users"),
            ("can_view_users", "Can view users"),
            ("can_create_users", "Can create users"),
            ("can_edit_users", "Can edit users"),
            ("can_delete_users", "Can delete users"),
            # Department management permissions
            ("can_manage_departments", "Can manage departments"),
            ("can_view_departments", "Can view departments"),
            ("can_create_departments", "Can create departments"),
            ("can_edit_departments", "Can edit departments"),
            ("can_delete_departments", "Can delete departments"),
            # Role management permissions
            ("can_manage_roles", "Can manage user roles"),
            ("can_assign_roles", "Can assign roles to users"),
            # System administration permissions
            ("can_access_admin", "Can access admin panel"),
            ("can_manage_system", "Can manage system settings"),
        ]

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        """Lấy tên đầy đủ"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username

    def get_role_display_name(self):
        """Lấy tên hiển thị của role"""
        return dict(UserRole.choices).get(self.role, self.role)

    def is_admin(self):
        """Kiểm tra có phải admin không"""
        return self.role == UserRole.ADMIN

    def is_manager(self):
        """Kiểm tra có phải manager không"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def is_hcns(self):
        """Kiểm tra có phải HCNS không"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS]

    def can_manage_users(self):
        """Kiểm tra có thể quản lý người dùng không"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def can_view_reports(self):
        """Kiểm tra có thể xem báo cáo không"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS]

    @property
    def is_admin_user(self):
        """Kiểm tra user có phải admin không"""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_manager_user(self):
        """Kiểm tra user có phải manager không"""
        return self.role == UserRole.MANAGER or self.is_superuser

    @property
    def is_hcns_user(self):
        """Kiểm tra user có phải HCNS không"""
        return self.role == UserRole.HCNS or self.is_superuser

    @property
    def is_employee_user(self):
        """Kiểm tra user có phải employee không"""
        return self.role == UserRole.EMPLOYEE

    def get_display_name(self):
        """Tên hiển thị của user"""
        return self.get_full_name()

    # Django Permissions Helper Methods
    def is_super_admin(self):
        """Kiểm tra có phải Super Admin không"""
        return self.is_superuser or self.groups.filter(name="Super Admin").exists()

    def is_admin_user_new(self):
        """Kiểm tra có phải Admin không (mới)"""
        return (
            self.is_superuser
            or self.groups.filter(name__in=["Super Admin", "Admin"]).exists()
        )

    def is_manager_user_new(self):
        """Kiểm tra có phải Manager không (mới)"""
        return (
            self.is_superuser
            or self.groups.filter(name__in=["Super Admin", "Admin", "Manager"]).exists()
        )

    def is_hr_user(self):
        """Kiểm tra có phải HR không"""
        return (
            self.is_superuser
            or self.groups.filter(
                name__in=["Super Admin", "Admin", "Manager", "HR"]
            ).exists()
        )

    def is_secretary_user(self):
        """Kiểm tra có phải Secretary không"""
        return (
            self.is_superuser
            or self.groups.filter(
                name__in=["Super Admin", "Admin", "Manager", "Secretary"]
            ).exists()
        )

    def is_employee_user_new(self):
        """Kiểm tra có phải Employee không (mới)"""
        return (
            self.is_superuser
            or self.groups.filter(
                name__in=[
                    "Super Admin",
                    "Admin",
                    "Manager",
                    "HR",
                    "Secretary",
                    "Employee",
                ]
            ).exists()
        )

    def can_manage_users_new(self):
        """Kiểm tra có thể quản lý users không (mới)"""
        return self.has_perm("users.can_manage_users")

    def can_view_users_new(self):
        """Kiểm tra có thể xem users không (mới)"""
        return self.has_perm("users.can_view_users")

    def can_manage_checkins_new(self):
        """Kiểm tra có thể quản lý checkins không (mới)"""
        return self.has_perm("checkin.can_manage_checkins")

    def can_view_all_checkins_new(self):
        """Kiểm tra có thể xem tất cả checkins không (mới)"""
        return self.has_perm("checkin.can_view_all_checkins")

    def can_manage_locations_new(self):
        """Kiểm tra có thể quản lý locations không (mới)"""
        return self.has_perm("location.can_manage_locations")

    def can_view_locations_new(self):
        """Kiểm tra có thể xem locations không (mới)"""
        return self.has_perm("location.can_view_locations")

    def can_manage_departments_new(self):
        """Kiểm tra có thể quản lý departments không (mới)"""
        return self.has_perm("users.can_manage_departments")

    # Management Structure Helper Methods
    def get_managed_offices(self):
        """Lấy danh sách văn phòng mà user này quản lý (Director/Deputy Director)"""
        from apps.users.models import Office

        return Office.objects.filter(
            models.Q(director=self) | models.Q(deputy_director=self)
        )

    def get_managed_departments(self):
        """Lấy danh sách phòng ban mà user này quản lý (Manager/Deputy Manager)"""
        from apps.users.models import Department

        return Department.objects.filter(
            models.Q(manager=self) | models.Q(deputy_manager=self)
        )

    def is_office_director(self, office=None):
        """Kiểm tra có phải Giám đốc Văn phòng không"""
        if office:
            return office.director == self
        from apps.users.models import Office

        return Office.objects.filter(director=self).exists()

    def is_office_deputy_director(self, office=None):
        """Kiểm tra có phải Phó Giám đốc Văn phòng không"""
        if office:
            return office.deputy_director == self
        from apps.users.models import Office

        return Office.objects.filter(deputy_director=self).exists()

    def is_department_manager(self, department=None):
        """Kiểm tra có phải Trưởng phòng không"""
        if department:
            return department.manager == self
        from apps.users.models import Department

        return Department.objects.filter(manager=self).exists()

    def is_department_deputy_manager(self, department=None):
        """Kiểm tra có phải Phó phòng không"""
        if department:
            return department.deputy_manager == self
        from apps.users.models import Department

        return Department.objects.filter(deputy_manager=self).exists()

    def can_view_office_data(self, office):
        """Kiểm tra có thể xem dữ liệu của văn phòng không"""
        return (
            self.is_superuser
            or self.is_office_director(office)
            or self.is_office_deputy_director(office)
            or self.is_admin_user
        )

    def can_view_department_data(self, department):
        """Kiểm tra có thể xem dữ liệu của phòng ban không"""
        return (
            self.is_superuser
            or self.is_department_manager(department)
            or self.is_department_deputy_manager(department)
            or self.can_view_office_data(department.office)
            or self.is_admin_user
        )

    def can_approve_absence_for_department(self, department):
        """Kiểm tra có thể phê duyệt đơn vắng mặt cho phòng ban không"""
        return (
            self.is_superuser
            or self.is_department_manager(department)
            or self.is_department_deputy_manager(department)
            or self.can_view_office_data(department.office)
            or self.is_hr_user
        )

    def get_approval_permissions(self):
        """Lấy danh sách quyền phê duyệt của user"""
        permissions = []

        # Office level permissions
        managed_offices = self.get_managed_offices()
        for office in managed_offices:
            if self.is_office_director(office):
                permissions.append(f"office_director_{office.id}")
            if self.is_office_deputy_director(office):
                permissions.append(f"office_deputy_{office.id}")

        # Department level permissions
        managed_departments = self.get_managed_departments()
        for department in managed_departments:
            if self.is_department_manager(department):
                permissions.append(f"department_manager_{department.id}")
            if self.is_department_deputy_manager(department):
                permissions.append(f"department_deputy_{department.id}")

        # HR permissions
        if self.is_hr_user():
            permissions.append("hr_approval")

        return permissions

    def can_view_checkin_reports_new(self):
        """Kiểm tra có thể xem báo cáo checkin không (mới)"""
        return self.has_perm("checkin.can_view_checkin_reports")

    def can_create_checkins_new(self):
        """Kiểm tra có thể tạo checkins không (mới)"""
        return self.has_perm("checkin.can_create_checkins")

    def can_view_own_checkins_new(self):
        """Kiểm tra có thể xem checkins của mình không (mới)"""
        return self.has_perm("checkin.can_view_own_checkins")
