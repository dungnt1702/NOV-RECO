from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

from .models import Checkin
from apps.location.models import Location
from apps.users.models import User
from apps.users.permissions import permission_required
from .serializers import CheckinListSerializer
from .utils import haversine_m, find_nearest_location


@login_required
def checkin_action_view(request):
    """Trang check-in chính"""
    areas = Location.objects.filter(is_active=True)
    context = {
        'areas': areas,
    }
    return render(request, 'checkin/action.html', context)


@login_required
@require_http_methods(["POST"])
def checkin_submit_view(request):
    """Xử lý submit check-in"""
    try:
        # Lấy dữ liệu từ form
        lat = float(request.POST.get('lat', 0))
        lng = float(request.POST.get('lng', 0))
        note = request.POST.get('note', '')
        area_id = request.POST.get('area_id')
        checkin_type = request.POST.get('checkin_type', '1')  # Default to '1' (Chấm công)
        address = request.POST.get('address', '')  # Địa chỉ từ reverse geocoding
        # Lấy ảnh
        photo = request.FILES.get('photo')
        if not photo:
            return JsonResponse(
                {'success': False, 'error': 'Vui lòng chụp ảnh'}, status=400
            )
        # Tự động tìm khu vực gần nhất dựa trên tọa độ
        area, distance = find_nearest_location(lat, lng, area_id)

        # Tạo check-in
        checkin = Checkin.objects.create(
            user=request.user,
            location=area,
            lat=lat,
            lng=lng,
            address=address,
            photo=photo,
            note=note,
            checkin_type=checkin_type,
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        # Tính khoảng cách
        if area:
            checkin.distance_m = haversine_m(area.lat, area.lng, lat, lng)
            checkin.save()

        # New pretty URL: /checkin/success/checkin_id/<id>/
        redirect_url = reverse(
            'checkin:success_by_id', kwargs={'checkin_id': checkin.id}
        )

        return JsonResponse({
            'success': True,
            'checkin_id': checkin.id,
            'area_name': (
                area.name
                if area else 'Không xác định'
            ),
            'area_id': area.id if area else None,
            'distance': distance if distance else checkin.distance_m,
            'redirect_url': redirect_url,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def checkin_success_view(request, checkin_id=None):
    """Trang thành công sau check-in"""
    checkin_id = checkin_id or request.GET.get('checkin_id')
    if checkin_id:
        try:
            checkin = Checkin.objects.get(id=checkin_id, user=request.user)
            success_data = {
                'user_name': checkin.user.get_full_name(),
                'user_email': checkin.user.email,
                'user_department': (
                    checkin.user.department.name
                    if checkin.user.department else 'N/A'
                ),
                'user_employee_id': checkin.user.username,
                'location_name': checkin.get_location_name(),
                'coordinates': (
                    f"{checkin.lat:.6f}, {checkin.lng:.6f}"
                ),
                'address': checkin.address or 'Không xác định',
                'checkin_time': checkin.created_at.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
                'note': checkin.note or '',
                'photo_url': (
                    checkin.photo.url if checkin.photo else None
                ),
            }
            context = {
                'checkin': checkin,
                'success_data': success_data,
                'location_name': checkin.get_location_name(),
                'distance': checkin.distance_m,
            }
            return render(request, 'checkin/success.html', context)
        except Checkin.DoesNotExist:
            pass

    # Default success data if no checkin_id provided
    success_data = {
        'user_name': request.user.get_full_name(),
        'user_email': request.user.email,
        'user_department': (
            request.user.department.name
            if request.user.department else 'N/A'
        ),
        'user_employee_id': request.user.username,
        'area_name': 'N/A',
        'coordinates': 'N/A',
        'checkin_time': 'N/A',
        'note': '',
        'photo_url': None,
    }
    context = {
        'success_data': success_data,
    }
    return render(request, 'checkin/success.html', context)


@login_required
def checkin_history_view(request):
    """Lịch sử check-in"""
    checkins = (Checkin.objects.filter(user=request.user)
                .select_related('location')
                .order_by('-created_at'))

    # Pagination
    paginator = Paginator(checkins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'checkins': page_obj,
    }
    return render(request, 'checkin/history.html', context)


@permission_required('checkin.can_view_all_checkins')
def checkin_list_view(request):
    """Danh sách check-in cho quản lý"""
    checkins = (Checkin.objects.select_related('user', 'area')
                .order_by('-created_at'))

    # Filtering
    search = request.GET.get('search', '')
    area_id = request.GET.get('area_id', '')
    user_id = request.GET.get('user_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        checkins = checkins.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(note__icontains=search)
        )

    if area_id:
        checkins = checkins.filter(location_id=area_id)

    if user_id:
        checkins = checkins.filter(user_id=user_id)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            checkins = checkins.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            checkins = checkins.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(checkins, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    areas = Location.objects.filter(is_active=True)
    users = (User.objects.filter(is_active=True)
             .order_by('first_name', 'last_name'))

    context = {
        'page_obj': page_obj,
        'checkins': page_obj,
        'areas': areas,
        'users': users,
        'search': search,
        'area_id': area_id,
        'user_id': user_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'checkin/list.html', context)


# API Views
@login_required
def checkin_list_api(request):
    """API danh sách check-in"""
    checkins = (Checkin.objects.select_related('user', 'area')
                .order_by('-created_at'))

    # Filtering
    search = request.GET.get('search', '')
    area_id = request.GET.get('area_id', '')
    user_id = request.GET.get('user_id', '')

    if search:
        checkins = checkins.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(note__icontains=search)
        )

    if area_id:
        checkins = checkins.filter(location_id=area_id)

    if user_id:
        checkins = checkins.filter(user_id=user_id)

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))

    paginator = Paginator(checkins, per_page)
    page_obj = paginator.get_page(page)

    serializer = CheckinListSerializer(page_obj, many=True)

    return JsonResponse({
        'checkins': serializer.data,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_count': paginator.count,
    })


def checkin_history_api(request):
    """API lịch sử check-in cho user hiện tại"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Chỉ lấy check-in của user hiện tại
    checkins = (Checkin.objects.filter(user=request.user)
                .select_related('location')
                .order_by('-created_at'))

    # Filtering
    search = request.GET.get('search', '')
    area_id = request.GET.get('area_id', '')

    if search:
        checkins = checkins.filter(
            Q(note__icontains=search) |
            Q(location__name__icontains=search)
        )

    if area_id:
        checkins = checkins.filter(location_id=area_id)

    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))

    paginator = Paginator(checkins, per_page)
    page_obj = paginator.get_page(page)

    serializer = CheckinListSerializer(page_obj, many=True)

    return JsonResponse({
        'checkins': serializer.data,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_count': paginator.count,
    })


@login_required
def checkin_user_info_api(request):
    """API thông tin user cho trang check-in"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'full_name': request.user.get_full_name(),
        'email': request.user.email,
        'role': request.user.role,
        'department': (request.user.department.name
                       if request.user.department else None),
        'avatar': request.user.avatar.url if request.user.avatar else None,
        'is_active': request.user.is_active,
    }

    return JsonResponse(user_data)

