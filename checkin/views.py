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
from .models import Location, Checkin, User, UserRole, Area
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
        "total_locations": Location.objects.count(),
        "total_areas": Area.objects.count(),
        "recent_checkins": Checkin.objects.select_related(
            "user", "area", "location"
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
            "user", "location"
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
        .select_related("location")
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
class LocationListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Lấy danh sách areas
        areas = list(
            Area.objects.filter(is_active=True).values(
                "id", "name", "lat", "lng", "radius_m"
            )
        )

        # Lấy danh sách locations
        locations = list(
            Location.objects.filter(is_active=True).values(
                "id", "name", "lat", "lng", "radius_m"
            )
        )

        # Kết hợp và trả về
        data = {"areas": areas, "locations": locations}
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
                    "location_name": checkin.get_location_name(),
                    "coordinates": f"{checkin.lat:.6f}, {checkin.lng:.6f}",
                    "checkin_time": checkin.created_at.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "note": checkin.note or "",
                    "photo_url": checkin.photo.url if checkin.photo else "",
                }

                # Redirect đến trang success với dữ liệu
                from urllib.parse import urlencode

                success_url = f"/checkin/success/?{urlencode(success_data)}"
                print(f"DEBUG: Redirecting to: {success_url}")
                return redirect(success_url)
            else:
                messages.error(request, f"Lỗi: {serializer.errors}")
                return redirect("/checkin/")

        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback

            traceback.print_exc()

            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return redirect("/checkin/")

    return redirect("/checkin/")


# Check-in list API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkin_list_api(request):
    """API để lấy danh sách check-in dựa trên quyền của người dùng"""
    user = request.user

    if user.can_view_all_checkins():
        # Admin và Manager có thể xem tất cả check-in
        checkins = Checkin.objects.select_related(
            "user", "area", "location"
        ).order_by("-created_at")
    else:
        # Nhân viên chỉ xem được check-in của mình
        checkins = (
            Checkin.objects.filter(user=user)
            .select_related("area", "location")
            .order_by("-created_at")
        )

    serializer = CheckinListSerializer(checkins, many=True)
    return Response(serializer.data)


# User management views
@admin_required
def user_management(request):
    """Quản lý người dùng - chỉ Admin"""
    users = User.objects.all().order_by("role", "first_name")
    context = {"users": users, "roles": UserRole.choices}
    return render(request, "checkin/user_management.html", context)


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


def checkin_success_view(request):
    """Trang kết quả check-in thành công"""
    return render(request, "checkin/checkin_success.html")


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
    location_id = request.GET.get("location")

    # Base queryset
    checkins = (
        Checkin.objects.filter(user=user)
        .select_related("area", "location")
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

    if location_id:
        try:
            # Filter by area or location
            checkins = checkins.filter(
                models.Q(area_id=int(location_id))
                | models.Q(location_id=int(location_id))
            )
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
                "location_name": checkin.get_location_name(),
                "distance_m": checkin.distance_m,
                "note": checkin.note,
                "photo_url": checkin.photo.url if checkin.photo else None,
                "ip": checkin.ip,
            }
        )

    return Response(
        {
            "checkins": checkin_data,
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
            .select_related("area", "location")
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
                "location_name": last_checkin.get_location_name(),
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
