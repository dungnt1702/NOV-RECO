from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Checkin
from apps.area.models import Area
from apps.users.models import User, UserRole
from .decorators import role_required
from .serializers import CheckinListSerializer
from .utils import haversine_m


@login_required
def checkin_action_view(request):
    """Trang check-in chính"""
    areas = Area.objects.filter(is_active=True)
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
        # Lấy ảnh
        photo = request.FILES.get('photo')
        if not photo:
            return JsonResponse(
                {'success': False, 'error': 'Vui lòng chụp ảnh'}, status=400
            )
        # Tìm khu vực gần nhất
        area = None
        if area_id:
            try:
                area = Area.objects.get(id=area_id)
            except Area.DoesNotExist:
                pass

        if not area:
            # Tìm khu vực gần nhất
            areas = Area.objects.filter(is_active=True)
            min_distance = float('inf')
            for a in areas:
                distance = haversine_m(a.lat, a.lng, lat, lng)
                if (distance < min_distance and
                        distance <= a.radius_m):
                    min_distance = distance
                    area = a

        # Tạo check-in
        checkin = Checkin.objects.create(
            user=request.user,
            area=area,
            lat=lat,
            lng=lng,
            photo=photo,
            note=note,
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        # Tính khoảng cách
        if area:
            checkin.distance_m = haversine_m(area.lat, area.lng, lat, lng)
            checkin.save()

        return JsonResponse({
            'success': True,
            'checkin_id': checkin.id,
            'area_name': area.name if area else 'Không xác định',
            'distance': checkin.distance_m
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def checkin_success_view(request):
    """Trang thành công sau check-in"""
    checkin_id = request.GET.get('checkin_id')
    if checkin_id:
        try:
            checkin = Checkin.objects.get(id=checkin_id, user=request.user)
            context = {
                'checkin': checkin,
                'area_name': checkin.get_area_name(),
                'distance': checkin.distance_m,
            }
            return render(request, 'checkin/success.html', context)
        except Checkin.DoesNotExist:
            pass

    return render(request, 'checkin/success.html')


@login_required
def checkin_history_view(request):
    """Lịch sử check-in"""
    checkins = (Checkin.objects.filter(user=request.user)
                .select_related('area')
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


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
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
        checkins = checkins.filter(area_id=area_id)

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
    areas = Area.objects.filter(is_active=True)
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
        checkins = checkins.filter(area_id=area_id)

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
                .select_related('area')
                .order_by('-created_at'))

    # Filtering
    search = request.GET.get('search', '')
    area_id = request.GET.get('area_id', '')

    if search:
        checkins = checkins.filter(
            Q(note__icontains=search) |
            Q(area__name__icontains=search)
        )

    if area_id:
        checkins = checkins.filter(area_id=area_id)

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
