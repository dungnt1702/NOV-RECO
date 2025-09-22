from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Checkin, Area
from users.models import User, UserRole
from .serializers import CheckinCreateSerializer, CheckinListSerializer
from .decorators import role_required


# Check-in action view (all authenticated users)
@login_required
def checkin_action_view(request):
    """Trang check-in cho tất cả người dùng"""
    return render(request, "checkin/action.html")


@login_required
def checkin_submit_view(request):
    """Xử lý submit check-in"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Parse form data
        data = {
            'user': request.user.id,
            'area': request.POST.get('area_id'),
            'lat': request.POST.get('lat'),
            'lng': request.POST.get('lng'),
            'note': request.POST.get('note', ''),
        }
        
        # Handle photo upload
        if 'photo' in request.FILES:
            data['photo'] = request.FILES['photo']

        serializer = CheckinCreateSerializer(data=data)
        if serializer.is_valid():
            checkin = serializer.save()
            # Return JSON response with redirect URL for AJAX
            return JsonResponse({
                "success": True,
                "redirect_url": f"/checkin/success/{checkin.id}/"
            })
        else:
            return JsonResponse({"error": serializer.errors}, status=400)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def checkin_success_view(request, checkin_id):
    """Trang thành công check-in"""
    try:
        checkin = Checkin.objects.select_related('user', 'area').get(id=checkin_id)
        
        # Verify user can view this checkin
        if not (request.user.is_admin() or request.user.is_manager() or checkin.user == request.user):
            messages.error(request, "Bạn không có quyền xem check-in này.")
            return redirect("checkin:history")
        
        success_data = {
            'user_name': checkin.user.get_display_name(),
            'user_email': checkin.user.email,
            'user_department': checkin.user.department.name if checkin.user.department else 'Chưa phân phòng ban',
            'user_employee_id': checkin.user.employee_id or 'Chưa có mã NV',
            'area_name': checkin.area.name,
            'coordinates': f"{checkin.lat:.6f}, {checkin.lng:.6f}",
            'checkin_time': checkin.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            'note': checkin.note or '',
            'photo_url': checkin.photo.url if checkin.photo else None
        }
        
        context = {
            'checkin': checkin,
            'success_data': success_data
        }
        return render(request, "checkin/success.html", context)
        
    except Checkin.DoesNotExist:
        messages.error(request, "Check-in không tồn tại.")
        return redirect("checkin:history")


@login_required
def checkin_history_view(request):
    """Lịch sử check-in cá nhân"""
    return render(request, "checkin/history.html")


@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.HCNS])
def checkin_list_view(request):
    """Danh sách check-in cho Thư ký, Quản lý, HCNS"""
    return render(request, "checkin/list.html")


# API Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkin_list_api(request):
    """API danh sách check-in"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    user_id = request.GET.get('user_id', '')
    area_id = request.GET.get('area_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build queryset
    if request.user.is_admin() or request.user.is_manager():
        # Admin/Manager can see all checkins
        queryset = Checkin.objects.select_related('user', 'area').all()
    else:
        # Others can only see their own checkins
        queryset = Checkin.objects.filter(user=request.user).select_related('user', 'area')
    
    # Apply filters
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if area_id:
        queryset = queryset.filter(area_id=area_id)
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    
    # Order by created_at desc
    queryset = queryset.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize data
    serializer = CheckinListSerializer(page_obj, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_history_api(request):
    """API lịch sử check-in của user"""
    from django.core.paginator import Paginator
    
    user_id = request.GET.get('user_id', request.user.id)
    
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or int(user_id) == request.user.id):
        return Response({"error": "Permission denied"}, status=403)
    
    # Get user's checkins
    queryset = Checkin.objects.filter(user_id=user_id).select_related('area').order_by('-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    serializer = CheckinListSerializer(page_obj, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def last_checkin_api(request):
    """API lấy check-in gần nhất"""
    user_id = request.GET.get('user_id', request.user.id)
    
    # Check permissions
    if not (request.user.is_admin() or request.user.is_manager() or int(user_id) == request.user.id):
        return Response({"error": "Permission denied"}, status=403)
    
    last_checkin = Checkin.objects.filter(user_id=user_id).select_related('area').order_by('-created_at').first()
    
    if last_checkin:
        serializer = CheckinListSerializer(last_checkin)
        return Response(serializer.data)
    else:
        return Response({"message": "No check-ins found"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info_api(request):
    """API thông tin user hiện tại"""
    from .serializers import UserSerializer
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
