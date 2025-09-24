from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Department, UserRole


class UserCreateForm(UserCreationForm):
    """Form tạo người dùng"""
    first_name = forms.CharField(max_length=30, required=True, label='Tên')
    last_name = forms.CharField(max_length=30, required=True, label='Họ')
    email = forms.EmailField(required=True, label='Email')
    employee_id = forms.CharField(max_length=20, required=False, label='Mã nhân viên')
    role = forms.ChoiceField(choices=UserRole.choices, label='Vai trò')
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Chọn phòng ban",
        label='Phòng ban'
    )
    phone = forms.CharField(max_length=20, required=False, label='Số điện thoại')
    date_of_birth = forms.DateField(required=False, label='Ngày sinh')
    gender = forms.ChoiceField(
        choices=[
            ('', 'Chọn giới tính'),
            ('male', 'Nam'),
            ('female', 'Nữ'),
            ('other', 'Khác'),
        ],
        required=False,
        label='Giới tính'
    )
    address = forms.CharField(widget=forms.Textarea, required=False, label='Địa chỉ')
    position = forms.CharField(max_length=100, required=False, label='Chức vụ')
    hire_date = forms.DateField(required=False, label='Ngày vào làm')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'employee_id', 'role', 'department',
            'phone', 'date_of_birth', 'gender', 'address', 'position', 'hire_date'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password2'].label = 'Xác nhận mật khẩu'


class UserUpdateForm(forms.ModelForm):
    """Form cập nhật người dùng"""
    first_name = forms.CharField(max_length=30, required=True, label='Tên')
    last_name = forms.CharField(max_length=30, required=True, label='Họ')
    email = forms.EmailField(required=True, label='Email')
    employee_id = forms.CharField(max_length=20, required=False, label='Mã nhân viên')
    role = forms.ChoiceField(choices=UserRole.choices, label='Vai trò')
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Chọn phòng ban",
        label='Phòng ban'
    )
    phone = forms.CharField(max_length=20, required=False, label='Số điện thoại')
    date_of_birth = forms.DateField(required=False, label='Ngày sinh')
    gender = forms.ChoiceField(
        choices=[
            ('', 'Chọn giới tính'),
            ('male', 'Nam'),
            ('female', 'Nữ'),
            ('other', 'Khác'),
        ],
        required=False,
        label='Giới tính'
    )
    address = forms.CharField(widget=forms.Textarea, required=False, label='Địa chỉ')
    emergency_contact = forms.CharField(max_length=100, required=False, label='Người liên hệ khẩn cấp')
    emergency_phone = forms.CharField(max_length=20, required=False, label='Số điện thoại liên hệ khẩn cấp')
    position = forms.CharField(max_length=100, required=False, label='Chức vụ')
    hire_date = forms.DateField(required=False, label='Ngày vào làm')
    salary = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='Lương')
    work_schedule = forms.CharField(max_length=100, required=False, label='Lịch làm việc')
    skills = forms.CharField(widget=forms.Textarea, required=False, label='Kỹ năng')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Ghi chú')
    is_active_employee = forms.BooleanField(required=False, label='Nhân viên đang hoạt động')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'employee_id', 'role', 'department',
            'phone', 'avatar', 'date_of_birth', 'gender', 'address',
            'emergency_contact', 'emergency_phone', 'position', 'hire_date',
            'salary', 'work_schedule', 'skills', 'notes', 'is_active_employee'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['is_active_employee'].initial = True


class DepartmentForm(forms.ModelForm):
    """Form phòng ban"""
    name = forms.CharField(max_length=100, required=True, label='Tên phòng ban')
    description = forms.CharField(widget=forms.Textarea, required=False, label='Mô tả')

    class Meta:
        model = Department
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            # Kiểm tra trùng lặp
            if self.instance.pk:
                if Department.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Tên phòng ban đã tồn tại')
            else:
                if Department.objects.filter(name=name).exists():
                    raise forms.ValidationError('Tên phòng ban đã tồn tại')
        return name
