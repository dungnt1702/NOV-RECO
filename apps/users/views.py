from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User, UserRole, Department, Office
from apps.users.forms import UserCreateForm, UserUpdateForm, DepartmentForm, OfficeForm
from apps.users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from apps.users.permissions import permission_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
import io
import csv


def debug_current_user(request):
    """Debug current user permissions"""
    if not request.user.is_authenticated:
        return render(request, 'debug_user.html', {'error': 'Not authenticated'})
    
    user = request.user
    context = {
        'user': user,
        'is_superuser': user.is_superuser,
        'groups': [g.name for g in user.groups.all()],
        'permissions': {
            'can_edit_users': user.has_perm('users.can_edit_users'),
            'can_view_users': user.has_perm('users.can_view_users'),
            'can_manage_users': user.has_perm('users.can_manage_users'),
        }
    }
    return render(request, 'debug_user.html', context)


@permission_required('users.can_view_users')
def user_list_view(request, office_id=None, department_id=None):
    """Danh sách người dùng"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter by department (prefer path param)
    dept_filter = department_id or request.GET.get('department')
    if dept_filter:
        users = users.filter(department_id=dept_filter)
    
    # Filter by office (through department)
    # Prefer path param office_id, fallback to query param
    office_filter = office_id or request.GET.get('office')
    # Infer office from department if missing
    if dept_filter and not office_filter:
        dept_obj = Department.objects.select_related('office').filter(id=dept_filter).first()
        if dept_obj and dept_obj.office_id:
            office_filter = str(dept_obj.office_id)
    if office_filter:
        users = users.filter(department__office_id=office_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.select_related('office').order_by('office__name', 'name')
    offices = Office.objects.all().order_by('name')
    
    context = {
        'users': page_obj,
        'departments': departments,
        'offices': offices,
        'role_choices': UserRole.choices,
        'current_role': role_filter,
        'current_dept': dept_filter,
        'current_office': office_filter,
        'current_search': search,
    }
    return render(request, 'users/user_list.html', context)


@permission_required('users.can_create_users')
def user_create_view(request):
    """Tạo người dùng mới"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Tạo người dùng {user.get_full_name()} thành công!')
            return redirect('users:list')
    else:
        form = UserCreateForm()
    
    departments = Department.objects.all()
    context = {
        'form': form,
        'departments': departments,
        'role_choices': UserRole.choices,
    }
    return render(request, 'users/create.html', context)


@permission_required('users.can_manage_users')
@require_http_methods(["GET", "POST"]) 
def user_import_view(request):
    """Import người dùng từ CSV (UTF-8, có BOM khuyến nghị)."""
    if request.method == 'GET':
        departments = Department.objects.select_related('office').order_by('office__name', 'name')
        context = {
            'departments': departments,
        }
        return render(request, 'users/import.html', context)
    
    # POST: handle upload
    file = request.FILES.get('file')
    default_department_id = request.POST.get('default_department')
    assign_default_department = request.POST.get('assign_default_department') == 'on'

    if not file:
        messages.error(request, 'Vui lòng chọn file (.xlsx hoặc .csv).')
        return redirect('users:import')

    created_count = 0
    updated_count = 0
    errors = []

    # Common expected headers
    expected_headers = ['username', 'first_name', 'last_name', 'email', 'role', 'employee_id', 'department_id']

    def process_rows(rows_iterable):
        nonlocal created_count, updated_count, errors
        with transaction.atomic():
            for idx, row in enumerate(rows_iterable, start=2):
                try:
                    username, first_name, last_name, email, role, employee_id, department_id = row
                    username = (username or '').strip()
                    if not username:
                        errors.append(f"Dòng {idx}: thiếu username")
                        continue
                    # Department resolution
                    dept_obj = None
                    if department_id not in (None, ''):
                        try:
                            dept_obj = Department.objects.get(id=int(department_id))
                        except Department.DoesNotExist:
                            errors.append(f"Dòng {idx}: department_id {department_id} không tồn tại")
                            dept_obj = None
                    if not dept_obj and assign_default_department and default_department_id:
                        try:
                            dept_obj = Department.objects.get(id=int(default_department_id))
                        except Department.DoesNotExist:
                            dept_obj = None

                    user, created = User.objects.update_or_create(
                        username=username,
                        defaults={
                            'first_name': (first_name or '').strip(),
                            'last_name': (last_name or '').strip(),
                            'email': (email or '').strip(),
                            'role': (role or 'employee').strip() or 'employee',
                            'employee_id': str(employee_id or '')[:50],
                            'department': dept_obj,
                            'is_active': True,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(f"Dòng {idx}: lỗi {e}")

    try:
        data = file.read().decode('utf-8-sig')  # UTF-8 with BOM safe
        reader = csv.reader(io.StringIO(data))
        header_row = next(reader, None) or []
        headers = [str(h).strip() for h in header_row]
        if [h.lower() for h in headers] != expected_headers:
            messages.error(request, 'Tiêu đề cột CSV không hợp lệ. Yêu cầu: ' + ', '.join(expected_headers))
            return redirect('users:import')
        process_rows(reader)
    except Exception as e:
        messages.error(request, f'Lỗi đọc CSV: {e}')
        return redirect('users:import')

    if created_count or updated_count:
        messages.success(request, f'Import thành công: tạo {created_count}, cập nhật {updated_count}.')
    if errors:
        messages.warning(request, 'Một số dòng lỗi:\n' + '\n'.join(errors[:10]) + ('' if len(errors) <= 10 else f"\n... và {len(errors)-10} lỗi khác"))

    return redirect('users:list')


@permission_required('users.can_manage_users')
@require_http_methods(["GET"]) 
def user_import_template_view(request):
    """Tải file CSV mẫu (UTF-8 BOM) cho import người dùng"""
    expected_headers = ['username', 'first_name', 'last_name', 'email', 'role', 'employee_id', 'department_id']
    sample_rows = [
        ['employee01', 'An', 'Nguyễn', 'an.nguyen@example.com', 'employee', 'EMP001', '12'],
        ['manager01', 'Bình', 'Trần', 'binh.tran@example.com', 'manager', 'EMP002', '13'],
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(expected_headers)
    for r in sample_rows:
        writer.writerow(r)
    content = output.getvalue()
    output.close()
    # Prepend UTF-8 BOM for Excel compatibility with Vietnamese characters
    bom = '\ufeff'
    from django.http import HttpResponse
    response = HttpResponse((bom + content), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="user_import_template.csv"'
    return response


@permission_required('users.can_edit_users')
def user_update_view(request, id):
    """Cập nhật thông tin người dùng"""
    target_user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cập nhật thông tin {target_user.get_full_name()} thành công!')
            return redirect('users:list')
    else:
        form = UserUpdateForm(instance=target_user)
    
    departments = Department.objects.all()
    context = {
        'form': form,
        'target_user': target_user,  # Đổi tên biến để tránh xung đột
        'departments': departments,
        'role_choices': UserRole.choices,
    }
    return render(request, 'users/update.html', context)


@permission_required('users.can_view_users')
def user_detail_view(request, id):
    """Chi tiết người dùng"""
    user = get_object_or_404(User, id=id)
    
    # Get user's check-ins
    from apps.checkin.models import Checkin
    checkins = Checkin.objects.filter(user=user).select_related('location').order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'checkins': checkins,
    }
    return render(request, 'users/detail.html', context)


@permission_required('users.can_edit_users')
def user_toggle_active_view(request, id):
    """Bật/tắt trạng thái hoạt động của người dùng"""
    user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status_text = "kích hoạt" if user.is_active else "vô hiệu hóa"
        messages.success(request, f'Đã {status_text} người dùng {user.get_full_name()}')
    
    return redirect('users:list')


@permission_required('users.can_delete_users')
def user_delete_view(request, id):
    """Xóa người dùng"""
    user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f'Đã xóa người dùng {user_name}')
        return redirect('users:list')
    
    context = {
        'user': user,
    }
    return render(request, 'users/delete.html', context)


@permission_required('users.can_view_departments')
def department_list_view(request, office_id=None):
    """Danh sách phòng ban"""
    departments = Department.objects.select_related('office').annotate(
        user_count=Count('user')
    ).order_by('office__name', 'name')
    
    # Filter by office (prefer path param)
    office_filter = office_id or request.GET.get('office')
    if office_filter:
        departments = departments.filter(office_id=office_filter)
    
    # Get all offices for filter dropdown
    offices = Office.objects.all().order_by('name')
    
    context = {
        'departments': departments,
        'offices': offices,
        'current_office': office_filter,
    }
    return render(request, 'users/department_list.html', context)


@permission_required('users.can_create_departments')
def department_create_view(request):
    """Tạo phòng ban mới"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Tạo phòng ban {department.name} thành công!')
            return redirect('users:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'users/department_create.html', context)


@permission_required('users.can_edit_departments')
def department_update_view(request, dept_id):
    """Cập nhật phòng ban"""
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Cập nhật phòng ban {department.name} thành công!')
            return redirect('users:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'department': department,
        'form': form,
    }
    return render(request, 'users/department_update.html', context)


@permission_required('users.can_delete_departments')
def department_delete_view(request, dept_id):
    """Xóa phòng ban"""
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == 'POST':
        dept_name = department.name
        department.delete()
        messages.success(request, f'Đã xóa phòng ban {dept_name}')
        return redirect('users:department_list')
    
    context = {
        'department': department,
    }
    return render(request, 'users/department_delete.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_api(request):
    """API danh sách người dùng"""
    users = User.objects.all()
    
    # Filter by department if provided
    department_id = request.GET.get('department')
    if department_id:
        users = users.filter(department_id=department_id)

    # Filter by office if provided (through department)
    office_id = request.GET.get('office')
    if office_id:
        users = users.filter(department__office_id=office_id)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_create_api(request):
    """API tạo người dùng"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_update_api(request, id):
    """API cập nhật người dùng"""
    user = get_object_or_404(User, id=id)
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_list_api(request):
    """API danh sách phòng ban (id, name, full_name, employee_count)."""
    departments = Department.objects.select_related('office').annotate(employee_count=Count('user')).order_by('office__name', 'name')
    data = [
        {
            'id': dept.id,
            'name': dept.name,
            'full_name': dept.full_name,
            'employee_count': dept.employee_count,
        }
        for dept in departments
    ]
    return Response(data)


# Office Management Views
@permission_required('users.can_view_offices')
def office_list_view(request):
    """Danh sách văn phòng"""
    offices = Office.objects.annotate(
        department_count=Count('department', distinct=True),
        user_count=Count('department__user', distinct=True)
    ).order_by('name')
    
    context = {
        'offices': offices,
    }
    return render(request, 'users/office_list.html', context)


@permission_required('users.can_create_offices')
def office_create_view(request):
    """Tạo văn phòng mới"""
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tạo văn phòng {form.instance.name} thành công!')
            return redirect('users:office_list')
        else:
            messages.error(request, 'Có lỗi xảy ra khi tạo văn phòng!')
    else:
        form = OfficeForm()
    
    users = User.objects.filter(groups__name__in=['Admin', 'Manager']).order_by('first_name', 'last_name')
    return render(request, 'users/office_create.html', {
        'form': form,
        'users': users
    })


@permission_required('users.can_edit_offices')
def office_update_view(request, office_id):
    """Cập nhật văn phòng"""
    office = get_object_or_404(Office, id=office_id)
    
    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cập nhật văn phòng {office.name} thành công!')
            return redirect('users:office_list')
        else:
            messages.error(request, 'Có lỗi xảy ra khi cập nhật văn phòng!')
    else:
        form = OfficeForm(instance=office)
    
    users = User.objects.filter(groups__name__in=['Admin', 'Manager']).order_by('first_name', 'last_name')
    context = {
        'office': office,
        'form': form,
        'users': users,
    }
    return render(request, 'users/office_update.html', context)


@permission_required('users.can_delete_offices')
def office_delete_view(request, office_id):
    """Xóa văn phòng"""
    office = get_object_or_404(Office, id=office_id)
    
    if request.method == 'POST':
        office_name = office.name
        office.delete()
        messages.success(request, f'Xóa văn phòng {office_name} thành công!')
        return redirect('users:office_list')
    
    context = {
        'office': office,
    }
    return render(request, 'users/office_delete.html', context)