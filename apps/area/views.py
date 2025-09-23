from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.area.models import Area
from .serializers import AreaSerializer
from apps.checkin.decorators import role_required
from apps.users.models import UserRole


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_list_view(request):
    """Danh sách khu vực"""
    areas = Area.objects.all().order_by('-created_at')
    
    context = {
        'areas': areas,
    }
    return render(request, 'area/list.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_create_view(request):
    """Tạo khu vực mới"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        radius_m = request.POST.get('radius_m', 100)
        
        if name and lat and lng:
            try:
                area = Area.objects.create(
                    name=name,
                    description=description,
                    lat=float(lat),
                    lng=float(lng),
                    radius_m=int(radius_m),
                    created_by=request.user
                )
                messages.success(request, f'Tạo khu vực {area.name} thành công!')
                return redirect('area:list')
            except ValueError:
                messages.error(request, 'Dữ liệu không hợp lệ!')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
    
    return render(request, 'area/create.html')


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_update_view(request, area_id):
    """Cập nhật khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    if request.method == 'POST':
        area.name = request.POST.get('name', area.name)
        area.description = request.POST.get('description', area.description)
        area.lat = float(request.POST.get('lat', area.lat))
        area.lng = float(request.POST.get('lng', area.lng))
        area.radius_m = int(request.POST.get('radius_m', area.radius_m))
        area.is_active = request.POST.get('is_active') == 'on'
        area.save()
        
        messages.success(request, f'Cập nhật khu vực {area.name} thành công!')
        return redirect('area:list')
    
    context = {
        'area': area,
    }
    return render(request, 'area/update.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_detail_view(request, area_id):
    """Chi tiết khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    # Get check-ins in this area
    from apps.checkin.models import Checkin
    checkins = Checkin.objects.filter(area=area).select_related('user').order_by('-created_at')[:10]
    
    context = {
        'area': area,
        'checkins': checkins,
    }
    return render(request, 'area/detail.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_delete_view(request, area_id):
    """Xóa khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    if request.method == 'POST':
        area_name = area.name
        area.delete()
        messages.success(request, f'Đã xóa khu vực {area_name}')
        return redirect('area:list')
    
    context = {
        'area': area,
    }
    return render(request, 'area/delete.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_toggle_active_view(request, area_id):
    """Bật/tắt trạng thái hoạt động của khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    if request.method == 'POST':
        area.is_active = not area.is_active
        area.save()
        
        status_text = "kích hoạt" if area.is_active else "vô hiệu hóa"
        messages.success(request, f'Đã {status_text} khu vực {area.name}')
    
    return redirect('area:list')


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_checkin_history_view(request, area_id):
    """Lịch sử check-in trong khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    from apps.checkin.models import Checkin
    checkins = Checkin.objects.filter(area=area).select_related('user').order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(checkins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'area': area,
        'checkins': page_obj,
    }
    return render(request, 'area/checkin_history.html', context)


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def area_statistics_view(request, area_id):
    """Thống kê khu vực"""
    area = get_object_or_404(Area, id=area_id)
    
    from apps.checkin.models import Checkin
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Thống kê check-in
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    today_checkins = Checkin.objects.filter(
        area=area,
        created_at__date=today
    ).count()
    
    week_checkins = Checkin.objects.filter(
        area=area,
        created_at__date__gte=week_start
    ).count()
    
    month_checkins = Checkin.objects.filter(
        area=area,
        created_at__date__gte=month_start
    ).count()
    
    total_checkins = Checkin.objects.filter(area=area).count()
    
    context = {
        'area': area,
        'today_checkins': today_checkins,
        'week_checkins': week_checkins,
        'month_checkins': month_checkins,
        'total_checkins': total_checkins,
    }
    return render(request, 'area/statistics.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def area_list_api(request):
    """API danh sách khu vực"""
    areas = Area.objects.filter(is_active=True)
    serializer = AreaSerializer(areas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def area_detail_api(request, area_id):
    """API chi tiết khu vực"""
    area = get_object_or_404(Area, id=area_id)
    serializer = AreaSerializer(area)
    return Response(serializer.data)