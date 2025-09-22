from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import JsonResponse
import os
from PIL import Image
from io import BytesIO
from apps.users.models import User, Department
from apps.checkin.decorators import role_required
from apps.users.models import UserRole


@login_required
def personal_profile_view(request):
    """Xem thông tin cá nhân"""
    user = request.user
    departments = Department.objects.all()
    
    context = {
        'user': user,
        'departments': departments,
    }
    return render(request, 'personal/profile.html', context)


@login_required
def personal_profile_edit_view(request):
    """Chỉnh sửa thông tin cá nhân"""
    user = request.user
    
    if request.method == 'POST':
        # Cập nhật thông tin cơ bản
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        user.date_of_birth = request.POST.get('date_of_birth') or None
        user.gender = request.POST.get('gender', '')
        user.emergency_contact = request.POST.get('emergency_contact', '')
        user.emergency_phone = request.POST.get('emergency_phone', '')
        user.position = request.POST.get('position', '')
        user.work_schedule = request.POST.get('work_schedule', '')
        user.skills = request.POST.get('skills', '')
        user.notes = request.POST.get('notes', '')
        
        # Cập nhật phòng ban nếu có quyền
        if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS]:
            department_id = request.POST.get('department')
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                    user.department = department
                except Department.DoesNotExist:
                    pass
        
        user.save()
        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('personal:profile')
    
    departments = Department.objects.all()
    context = {
        'user': user,
        'departments': departments,
    }
    return render(request, 'personal/profile_edit.html', context)


@login_required
def personal_avatar_upload_view(request):
    """Upload avatar"""
    if request.method == 'POST':
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            
            # Validate file type
            if not avatar_file.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': 'File phải là hình ảnh'})
            
            # Validate file size (max 5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'message': 'File quá lớn (tối đa 5MB)'})
            
            try:
                # Process image
                image = Image.open(avatar_file)
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Resize to 300x300
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Save to BytesIO
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                # Delete old avatar if exists
                if request.user.avatar:
                    try:
                        if os.path.isfile(request.user.avatar.path):
                            os.remove(request.user.avatar.path)
                    except:
                        pass
                
                # Save new avatar
                request.user.avatar.save(
                    f'avatar_{request.user.id}.jpg',
                    ContentFile(output.getvalue()),
                    save=True
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Cập nhật avatar thành công!',
                    'avatar_url': request.user.avatar.url
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Lỗi xử lý ảnh: {str(e)}'})
        
        return JsonResponse({'success': False, 'message': 'Không có file được chọn'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})


@login_required
def personal_password_change_view(request):
    """Đổi mật khẩu"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Mật khẩu hiện tại không đúng!')
            return render(request, 'personal/password_change.html')
        
        # Validate new password
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới không khớp!')
            return render(request, 'personal/password_change.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 8 ký tự!')
            return render(request, 'personal/password_change.html')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Đổi mật khẩu thành công!')
        return redirect('personal:profile')
    
    return render(request, 'personal/password_change.html')


@login_required
def personal_checkin_history_view(request):
    """Lịch sử check-in cá nhân"""
    user = request.user
    checkins = user.checkin_set.select_related('area').order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(checkins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'checkins': page_obj,
    }
    return render(request, 'personal/checkin_history.html', context)