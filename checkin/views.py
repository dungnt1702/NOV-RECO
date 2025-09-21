from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import models
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from .models import Checkin, Area
from users.models import User, UserRole
from .serializers import (
    CheckinCreateSerializer,
    CheckinListSerializer,
    UserSerializer,
    AreaSerializer,
)
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
        messages.error(request, "Vai trò người dùng không hợp lệ.")
        return redirect("home")


@admin_required
def admin_dashboard(request):
    """Dashboard cho Admin"""
    context = {
        "total_users": User.objects.count(),
        "total_checkins": Checkin.objects.count(),
        "total_areas": Area.objects.count(),
        "recent_checkins": Checkin.objects.select_related(
            "user", "area"
        ).order_by("-created_at")[:10],
        "users_by_role": {
            "admin": User.objects.filter(role=UserRole.ADMIN).count(),
            "manager": User.objects.filter(role=UserRole.MANAGER).count(),
            "employee": User.objects.filter(role=UserRole.EMPLOYEE).count(),
        },
    }
    return render(request, "checkin/admin_dashboard.html", context)


@manager_required
def manager_dashboard(request):
    """Dashboard cho Quản lý"""
    context = {
        "total_employees": User.objects.filter(role=UserRole.EMPLOYEE).count(),
        "total_checkins": Checkin.objects.count(),
        "recent_checkins": Checkin.objects.select_related(
            "user", "area"
        ).order_by("-created_at")[:10],
        "employees": User.objects.filter(role=UserRole.EMPLOYEE).order_by(
            "first_name"
        ),
    }
    return render(request, "checkin/manager_dashboard.html", context)


@employee_required
def employee_dashboard(request):
    """Dashboard cho Nhân viên"""
    user = request.user
    context = {
        "user_checkins": Checkin.objects.filter(user=user)
        .select_related("area")
        .order_by("-created_at")[:10],
        "total_checkins": Checkin.objects.filter(user=user).count(),
        "recent_checkin": Checkin.objects.filter(user=user)
        .order_by("-created_at")
        .first(),
    }
    return render(request, "checkin/employee_dashboard.html", context)


# Check-in views
@employee_required
def checkin_page(request):
    return render(request, "checkin/checkin.html")


# API Views
@method_decorator(login_required, name="dispatch")
class AreaListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Lấy danh sách areas
        areas = list(
            Area.objects.filter(is_active=True).values(
                "id", "name", "lat", "lng", "radius_m"
            )
        )

        # Trả về danh sách areas
        data = {"areas": areas}
        return Response(data)


@method_decorator(login_required, name="dispatch")
class CheckinCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckinCreateSerializer
    parser_classes = [MultiPartParser, FormParser]


@login_required
def checkin_submit_view(request):
    """Xử lý form submit check-in và redirect đến trang success"""
    if request.method == "POST":
        print(f"DEBUG: Received POST request from {request.user}")
        print(f"DEBUG: Request POST: {request.POST}")
        print(f"DEBUG: Request FILES: {request.FILES}")

        try:
            # Với FormData từ JavaScript, cần xử lý đặc biệt
            data = request.POST.copy()
            files = request.FILES

            print(f"DEBUG: Data before processing: {data}")
            print(f"DEBUG: Files: {files}")

            # Thêm files vào data
            for key, file in files.items():
                data[key] = file
                print(f"DEBUG: Added file {key}: {file}")

            print(f"DEBUG: Final data: {data}")

            serializer = CheckinCreateSerializer(
                data=data, context={"request": request}
            )

            print(f"DEBUG: Serializer is_valid: {serializer.is_valid()}")
            if not serializer.is_valid():
                print(f"DEBUG: Serializer errors: {serializer.errors}")

            if serializer.is_valid():
                # Tạo check-in
                checkin = serializer.save()
                print(f"DEBUG: Check-in created with ID: {checkin.id}")

                # Chuẩn bị dữ liệu cho trang success
                success_data = {
                    "user_name": checkin.user.get_display_name(),
                    "user_email": checkin.user.email,
                    "user_department": checkin.user.department or "N/A",
                    "user_employee_id": checkin.user.employee_id or "N/A",
                    "area_name": checkin.get_area_name(),
                    "coordinates": f"{checkin.lat:.6f}, {checkin.lng:.6f}",
                    "checkin_time": checkin.created_at.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "note": checkin.note or "",
                    "photo_url": checkin.photo.url if checkin.photo else "",
                }

                # Redirect đến trang success với professional URL pattern
                success_url = f"/checkin/success/{checkin.id}/"
                print(f"DEBUG: Redirecting to: {success_url}")
                return redirect(success_url)
            else:
                messages.error(request, f"Lỗi: {serializer.errors}")
                return redirect("/checkin/action/")

        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback

            traceback.print_exc()

            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return redirect("/checkin/action/")

    return redirect("/checkin/action/")


# Check-in list API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkin_list_api(request):
    """API để lấy danh sách check-in dựa trên quyền của người dùng"""
    user = request.user

    if user.can_view_all_checkins():
        # Admin và Manager có thể xem tất cả check-in
        checkins = Checkin.objects.select_related(
            "user", "area"
        ).order_by("-created_at")
    else:
        # Nhân viên chỉ xem được check-in của mình
        checkins = (
            Checkin.objects.filter(user=user)
            .select_related("area")
            .order_by("-created_at")
        )

    serializer = CheckinListSerializer(checkins, many=True)
    return Response({
        "results": serializer.data,
        "count": len(serializer.data)
    })


# User info API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info_api(request):
    """API để lấy thông tin người dùng hiện tại"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


# Check-in list view
@manager_required
def checkin_list_view(request):
    """Trang danh sách check-in cho Manager và Admin"""
    return render(request, "checkin/checkin_list.html")


@login_required
def checkin_success_view(request, checkin_id):
    """Trang kết quả check-in thành công"""
    if not checkin_id:
        messages.error(request, "Không tìm thấy thông tin check-in")
        return redirect('/checkin/action/')
    
    try:
        # Lookup checkin data from database
        checkin = Checkin.objects.select_related('user', 'area').get(
            id=checkin_id, 
            user=request.user  # Security: only show user's own checkin
        )
        
        # Pass data to template context instead of URL
        context = {
            'checkin': checkin,
            'success_data': {
                'user_name': checkin.user.get_display_name(),
                'user_email': checkin.user.email,
                'user_department': checkin.user.department.name if checkin.user.department else 'N/A',
                'user_employee_id': checkin.user.employee_id or 'N/A',
                'area_name': checkin.get_area_name(),
                'coordinates': f"{checkin.lat:.6f}, {checkin.lng:.6f}",
                'checkin_time': checkin.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                'note': checkin.note or '',
                'photo_url': checkin.photo.url if checkin.photo else ''
            }
        }
        
        print(f"DEBUG: Context data: {context['success_data']}")  # Debug output
        
        return render(request, "checkin/checkin_success.html", context)
        
    except Checkin.DoesNotExist:
        messages.error(request, "Check-in không tồn tại hoặc bạn không có quyền xem")
        return redirect('/checkin/action/')


def debug_mobile_cards_view(request):
    """Debug view for mobile cards issue"""
    from django.http import HttpResponse
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Mobile Cards</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .debug-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
            .error { color: red; }
            .success { color: green; }
            .info { color: blue; }
        </style>
    </head>
    <body>
        <h1>🔍 Debug Mobile Cards</h1>
        
        <div class="debug-section">
            <h3>1. Screen Width Test</h3>
            <p>Screen width: <span id="screen-width"></span>px</p>
            <p>Is mobile: <span id="is-mobile"></span></p>
        </div>
        
        <div class="debug-section">
            <h3>2. JavaScript Files Test</h3>
            <p>base.js loaded: <span id="base-js-status"></span></p>
            <p>api function: <span id="api-function-status"></span></p>
        </div>
        
        <div class="debug-section">
            <h3>3. API Test</h3>
            <button onclick="testAPI()">Test API</button>
            <div id="api-result"></div>
        </div>
        
        <div class="debug-section">
            <h3>4. Mobile Cards Container</h3>
            <div class="mobile-cards" id="mobile-cards" style="border: 1px solid blue; min-height: 100px;">
                Mobile cards will appear here...
            </div>
        </div>

        <script>
            // Test 1: Screen width
            document.getElementById('screen-width').textContent = window.innerWidth;
            document.getElementById('is-mobile').textContent = window.innerWidth <= 768 ? 'YES' : 'NO';
            
            // Test 2: JavaScript files
            document.getElementById('base-js-status').textContent = typeof api !== 'undefined' ? '✅ Loaded' : '❌ Missing';
            document.getElementById('api-function-status').textContent = typeof api === 'function' ? '✅ Function OK' : '❌ Not function';
            
            // Test 3: API test function with fallback fetch
            async function testAPI() {
                const resultDiv = document.getElementById('api-result');
                resultDiv.innerHTML = '<p class="info">Testing API...</p>';
                
                try {
                    let response;
                    
                    if (typeof api === 'function') {
                        response = await api('/checkin/list/');
                    } else {
                        // Fallback to fetch if api() not available
                        response = await fetch('/checkin/list/', {
                            method: 'GET',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'Content-Type': 'application/json'
                            }
                        });
                    }
                    
                    console.log('API Response:', response);
                    
                    if (response.ok) {
                        const responseData = await response.json();
                        console.log('Response data:', responseData);
                        
                        // Handle both array format (local) and object format (server)
                        const data = Array.isArray(responseData) ? responseData : responseData.results || [];
                        
                        resultDiv.innerHTML = `
                            <p class="success">✅ API Success!</p>
                            <p>Response type: ${Array.isArray(responseData) ? 'Array' : 'Object'}</p>
                            <p>Data count: ${data.length}</p>
                            <pre>${JSON.stringify(responseData, null, 2).substring(0, 500)}...</pre>
                        `;
                        
                        // Test mobile cards rendering
                        renderTestMobileCards(data.slice(0, 3));
                    } else {
                        resultDiv.innerHTML = `<p class="error">❌ API Error: ${response.status} ${response.statusText}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<p class="error">❌ Exception: ${error.message}</p>`;
                    console.error('API Test Error:', error);
                }
            }
            
            // Test mobile cards rendering
            function renderTestMobileCards(checkins) {
                const container = document.getElementById('mobile-cards');
                container.innerHTML = checkins.map(checkin => `
                    <div style="border: 1px solid green; padding: 10px; margin: 5px;">
                        <strong>${checkin.user_name}</strong><br>
                        Area: ${checkin.area_name}<br>
                        Time: ${checkin.created_at}<br>
                        Photo: ${checkin.photo_url ? '✅ Has photo' : '❌ No photo'}
                    </div>
                `).join('');
            }
        </script>
        
        <!-- Try multiple ways to load base.js -->
        <script src="/static/js/base.js" onerror="console.error('Failed to load base.js from /static/js/base.js')"></script>
        <script src="{% static 'js/base.js' %}" onerror="console.error('Failed to load base.js from Django static')"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)


@login_required
def user_history_view(request):
    """Trang lịch sử check-in của user"""
    return render(request, "checkin/user_history.html")


@login_required
def quick_checkin_view(request):
    """Trang check-in nhanh sử dụng dữ liệu từ lần check-in trước"""
    return render(request, "checkin/quick_checkin.html")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_history_api(request):
    """API để lấy lịch sử check-in của user hiện tại"""
    from django.core.paginator import Paginator
    from datetime import datetime, timedelta

    user = request.user

    # Get filter parameters
    page = int(request.GET.get("page", 1))
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    area_id = request.GET.get("area")

    # Base queryset
    checkins = (
        Checkin.objects.filter(user=user)
        .select_related("area")
        .order_by("-created_at")
    )

    # Apply filters
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            checkins = checkins.filter(created_at__date__gte=from_date_obj)
        except ValueError:
            pass

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
            checkins = checkins.filter(created_at__date__lte=to_date_obj)
        except ValueError:
            pass

    if area_id:
        try:
            # Filter by area
            checkins = checkins.filter(area_id=int(area_id))
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(checkins, 10)  # 10 items per page
    page_obj = paginator.get_page(page)

    # Calculate stats
    now = datetime.now()
    this_month = now.replace(day=1)
    this_week = now - timedelta(days=now.weekday())

    stats = {
        "total_count": paginator.count,
        "this_month": checkins.filter(created_at__gte=this_month).count(),
        "this_week": checkins.filter(created_at__gte=this_week).count(),
    }

    # Serialize checkins
    checkin_data = []
    for checkin in page_obj:
        checkin_data.append(
            {
                "id": checkin.id,
                "created_at": checkin.created_at.isoformat(),
                "lat": float(checkin.lat),
                "lng": float(checkin.lng),
                "area_name": checkin.get_area_name(),
                "distance_m": checkin.distance_m,
                "note": checkin.note,
                "photo_url": checkin.photo.url if checkin.photo else None,
                "ip": checkin.ip,
                "user_name": checkin.user.get_display_name(),
                "user_email": checkin.user.email,
            }
        )

    return Response(
        {
            "results": checkin_data,
            "total_pages": paginator.num_pages,
            "current_page": page,
            **stats,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def last_checkin_api(request):
    """API để lấy dữ liệu check-in cuối cùng của user"""
    user = request.user

    try:
        last_checkin = (
            Checkin.objects.filter(user=user)
            .select_related("area")
            .order_by("-created_at")
            .first()
        )

        if not last_checkin:
            return Response({"error": "Không có check-in nào"}, status=404)

        return Response(
            {
                "id": last_checkin.id,
                "lat": float(last_checkin.lat),
                "lng": float(last_checkin.lng),
                "area_name": last_checkin.get_area_name(),
                "coordinates": (
                    f"{last_checkin.lat:.6f}, {last_checkin.lng:.6f}"
                ),
                "checkin_time": last_checkin.created_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),
                "note": last_checkin.note or "",
                "photo_url": (
                    last_checkin.photo.url if last_checkin.photo else None
                ),
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# Users API for filter
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_api(request):
    """API để lấy danh sách người dùng cho filter"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return Response({"error": "Permission denied"}, status=403)

    users = User.objects.filter(is_active=True).order_by("first_name")
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# Area Management APIs
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def areas_api(request):
    """API để quản lý khu vực"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return Response({"error": "Permission denied"}, status=403)

    if request.method == "GET":
        areas = Area.objects.all().order_by("-created_at")
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def area_detail_api(request, area_id):
    """API để quản lý chi tiết khu vực"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return Response({"error": "Permission denied"}, status=403)

    try:
        area = Area.objects.get(id=area_id)
    except Area.DoesNotExist:
        return Response({"error": "Khu vực không tồn tại"}, status=404)

    if request.method == "GET":
        serializer = AreaSerializer(area)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = AreaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        area.delete()
        return Response({"message": "Khu vực đã được xóa"}, status=200)


@admin_required
def area_management(request):
    """Trang quản lý khu vực cho Admin"""
    return render(request, "checkin/area_management.html")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_checkins_areas_api(request):
    """API để cập nhật tất cả check-in dựa trên area hiện có"""
    from django.core.management import call_command
    from io import StringIO
    import sys

    if not request.user.can_view_all_checkins():
        return Response(
            {"error": "Không có quyền thực hiện thao tác này"}, status=403
        )

    try:
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        # Run the command
        call_command("update_all_checkins_areas")

        # Get output
        output = captured_output.getvalue()
        sys.stdout = old_stdout

        return Response(
            {"message": "Đã cập nhật check-in thành công", "output": output}
        )

    except Exception as e:
        sys.stdout = old_stdout
        return Response(
            {"error": f"Lỗi cập nhật check-in: {str(e)}"}, status=500
        )
