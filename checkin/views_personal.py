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
from users.models import User, Department
from .decorators import role_required
from users.models import UserRole


@login_required
def personal_profile_view(request):
    """Trang thông tin cá nhân"""
    user = request.user
    departments = Department.objects.all().order_by('name')
    
    context = {
        'user': user,
        'departments': departments,
        'gender_choices': User._meta.get_field('gender').choices,
    }
    return render(request, "personal/profile.html", context)


@login_required
def personal_edit_view(request):
    """Chỉnh sửa thông tin cá nhân"""
    user = request.user
    departments = Department.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Cập nhật thông tin cơ bản
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        
        # Thông tin cá nhân
        user.date_of_birth = request.POST.get('date_of_birth') or None
        user.gender = request.POST.get('gender', '')
        user.address = request.POST.get('address', '')
        user.emergency_contact = request.POST.get('emergency_contact', '')
        user.emergency_phone = request.POST.get('emergency_phone', '')
        
        # Thông tin công việc (chỉ user có thể sửa một số thông tin)
        user.position = request.POST.get('position', '')
        user.skills = request.POST.get('skills', '')
        user.notes = request.POST.get('notes', '')
        
        # Xử lý avatar
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            
            # Kiểm tra kích thước file (max 5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                messages.error(request, "Kích thước ảnh không được vượt quá 5MB.")
                return redirect('personal:edit')
            
            # Kiểm tra định dạng file
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar_file.content_type not in allowed_types:
                messages.error(request, "Chỉ chấp nhận file ảnh JPG, PNG, GIF.")
                return redirect('personal:edit')
            
            # Xóa avatar cũ nếu có
            if user.avatar:
                try:
                    if os.path.isfile(user.avatar.path):
                        os.remove(user.avatar.path)
                except:
                    pass
            
            # Lưu avatar mới
            user.avatar = avatar_file
            
            # Resize ảnh nếu cần
            try:
                img = Image.open(avatar_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize về 300x300
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Lưu lại
                output = BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                user.avatar.save(
                    f"avatar_{user.id}.jpg",
                    ContentFile(output.getvalue()),
                    save=False
                )
            except Exception as e:
                messages.warning(request, f"Có lỗi khi xử lý ảnh: {str(e)}")
        
        try:
            user.save()
            messages.success(request, "Cập nhật thông tin cá nhân thành công!")
            return redirect('personal:profile')
        except Exception as e:
            messages.error(request, f"Có lỗi khi cập nhật: {str(e)}")
    
    context = {
        'user': user,
        'departments': departments,
        'gender_choices': User._meta.get_field('gender').choices,
    }
    return render(request, "personal/edit.html", context)


@login_required
def personal_change_password_view(request):
    """Đổi mật khẩu"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Kiểm tra mật khẩu hiện tại
        if not request.user.check_password(current_password):
            messages.error(request, "Mật khẩu hiện tại không đúng.")
            return redirect('personal:change_password')
        
        # Kiểm tra mật khẩu mới
        if new_password != confirm_password:
            messages.error(request, "Mật khẩu mới và xác nhận không khớp.")
            return redirect('personal:change_password')
        
        if len(new_password) < 8:
            messages.error(request, "Mật khẩu mới phải có ít nhất 8 ký tự.")
            return redirect('personal:change_password')
        
        # Cập nhật mật khẩu
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, "Đổi mật khẩu thành công! Vui lòng đăng nhập lại.")
        return redirect('account_login')
    
    return render(request, "personal/change_password.html")


@login_required
def personal_avatar_upload_view(request):
    """API upload avatar"""
    if request.method == 'POST' and 'avatar' in request.FILES:
        avatar_file = request.FILES['avatar']
        
        # Kiểm tra kích thước và định dạng
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'Kích thước ảnh quá lớn'}, status=400)
        
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({'error': 'Định dạng ảnh không được hỗ trợ'}, status=400)
        
        # Xóa avatar cũ
        if request.user.avatar:
            try:
                if os.path.isfile(request.user.avatar.path):
                    os.remove(request.user.avatar.path)
            except:
                pass
        
        # Lưu avatar mới
        request.user.avatar = avatar_file
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'avatar_url': request.user.avatar.url
        })
    
    return JsonResponse({'error': 'Không có file ảnh'}, status=400)
