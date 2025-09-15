from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from .models import Location, Checkin, User, UserRole
from .serializers import CheckinCreateSerializer, CheckinListSerializer
from .decorators import admin_required, manager_required, employee_required

# Dashboard views
@login_required
def dashboard(request):
    """Dashboard chính dựa trên vai trò người dùng"""
    user = request.user
    
    if user.is_admin():
        return admin_dashboard(request)
    elif user.is_manager():
        return manager_dashboard(request)
    elif user.is_employee():
        return employee_dashboard(request)
    else:
        messages.error(request, 'Vai trò người dùng không hợp lệ.')
        return redirect('home')

@admin_required
def admin_dashboard(request):
    """Dashboard cho Admin"""
    context = {
        'total_users': User.objects.count(),
        'total_checkins': Checkin.objects.count(),
        'total_locations': Location.objects.count(),
        'recent_checkins': Checkin.objects.select_related('user', 'location').order_by('-created_at')[:10],
        'users_by_role': {
            'admin': User.objects.filter(role=UserRole.ADMIN).count(),
            'manager': User.objects.filter(role=UserRole.MANAGER).count(),
            'employee': User.objects.filter(role=UserRole.EMPLOYEE).count(),
        }
    }
    return render(request, 'checkin/admin_dashboard.html', context)

@manager_required
def manager_dashboard(request):
    """Dashboard cho Quản lý"""
    context = {
        'total_employees': User.objects.filter(role=UserRole.EMPLOYEE).count(),
        'total_checkins': Checkin.objects.count(),
        'recent_checkins': Checkin.objects.select_related('user', 'location').order_by('-created_at')[:10],
        'employees': User.objects.filter(role=UserRole.EMPLOYEE).order_by('first_name')
    }
    return render(request, 'checkin/manager_dashboard.html', context)

@employee_required
def employee_dashboard(request):
    """Dashboard cho Nhân viên"""
    user = request.user
    context = {
        'user_checkins': Checkin.objects.filter(user=user).select_related('location').order_by('-created_at')[:10],
        'total_checkins': Checkin.objects.filter(user=user).count(),
        'recent_checkin': Checkin.objects.filter(user=user).order_by('-created_at').first()
    }
    return render(request, 'checkin/employee_dashboard.html', context)

# Check-in views
@employee_required
def checkin_page(request):
    return render(request, "checkin/checkin.html")

# API Views
@method_decorator(login_required, name='dispatch')
class LocationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        data = list(Location.objects.filter(is_active=True).values("id","name","lat","lng","radius_m"))
        return Response(data)

@method_decorator(login_required, name='dispatch')
class CheckinCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckinCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

# Check-in list API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkin_list_api(request):
    """API để lấy danh sách check-in dựa trên quyền của người dùng"""
    user = request.user
    
    if user.can_view_all_checkins():
        # Admin và Manager có thể xem tất cả check-in
        checkins = Checkin.objects.select_related('user', 'location').order_by('-created_at')
    else:
        # Nhân viên chỉ xem được check-in của mình
        checkins = Checkin.objects.filter(user=user).select_related('location').order_by('-created_at')
    
    serializer = CheckinListSerializer(checkins, many=True)
    return Response(serializer.data)

# User management views
@admin_required
def user_management(request):
    """Quản lý người dùng - chỉ Admin"""
    users = User.objects.all().order_by('role', 'first_name')
    context = {
        'users': users,
        'roles': UserRole.choices
    }
    return render(request, 'checkin/user_management.html', context)
