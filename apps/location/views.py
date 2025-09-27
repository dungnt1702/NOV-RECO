from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.location.models import Location
from apps.users.permissions import permission_required

from .serializers import LocationSerializer


@permission_required("location.can_view_locations")
def location_list_view(request):
    """Danh sách địa điểm"""
    locations = Location.objects.all().order_by("-created_at")

    context = {
        "locations": locations,
    }
    return render(request, "location/list.html", context)


@permission_required("location.can_create_locations")
def location_create_view(request):
    """Tạo địa điểm mới"""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        address = request.POST.get("address", "")
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        radius_m = request.POST.get("radius_m", 100)

        if name and lat and lng:
            try:
                location = Location.objects.create(
                    name=name,
                    description=description,
                    address=address,
                    lat=float(lat),
                    lng=float(lng),
                    radius_m=int(radius_m),
                    created_by=request.user,
                )
                messages.success(request, f"Tạo địa điểm {location.name} thành công!")
                return redirect("location:list")
            except ValueError:
                messages.error(request, "Dữ liệu không hợp lệ!")
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin!")

    return render(request, "location/create.html")


@permission_required("location.can_edit_locations")
def location_update_view(request, location_id):
    """Cập nhật địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    if request.method == "POST":
        location.name = request.POST.get("name", location.name)
        location.description = request.POST.get("description", location.description)
        location.address = request.POST.get("address", location.address)
        location.lat = float(request.POST.get("lat", location.lat))
        location.lng = float(request.POST.get("lng", location.lng))
        location.radius_m = int(request.POST.get("radius_m", location.radius_m))
        location.is_active = request.POST.get("is_active") == "on"
        location.save()

        messages.success(request, f"Cập nhật địa điểm {location.name} thành công!")
        return redirect("location:list")

    context = {
        "location": location,
    }
    return render(request, "location/update.html", context)


@permission_required("location.can_view_locations")
def location_detail_view(request, location_id):
    """Chi tiết địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    # Get check-ins in this location
    from apps.checkin.models import Checkin

    checkins = (
        Checkin.objects.filter(location=location)
        .select_related("user")
        .order_by("-created_at")[:10]
    )

    context = {
        "location": location,
        "checkins": checkins,
    }
    return render(request, "location/detail.html", context)


@permission_required("location.can_delete_locations")
def location_delete_view(request, location_id):
    """Xóa địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    if request.method == "POST":
        location_name = location.name
        location.delete()
        messages.success(request, f"Đã xóa địa điểm {location_name}")
        return redirect("location:list")

    context = {
        "location": location,
    }
    return render(request, "location/delete.html", context)


@permission_required("location.can_activate_locations")
def location_toggle_active_view(request, location_id):
    """Bật/tắt trạng thái hoạt động của địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    if request.method == "POST":
        location.is_active = not location.is_active
        location.save()

        status_text = "kích hoạt" if location.is_active else "vô hiệu hóa"
        messages.success(request, f"Đã {status_text} địa điểm {location.name}")

    return redirect("location:list")


@permission_required("checkin.can_view_checkin_reports")
def location_checkin_history_view(request, location_id):
    """Lịch sử check-in trong địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    from apps.checkin.models import Checkin

    checkins = (
        Checkin.objects.filter(location=location)
        .select_related("user")
        .order_by("-created_at")
    )

    # Pagination
    from django.core.paginator import Paginator

    paginator = Paginator(checkins, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "location": location,
        "checkins": page_obj,
    }
    return render(request, "location/checkin_history.html", context)


@permission_required("checkin.can_view_checkin_reports")
def location_statistics_view(request, location_id):
    """Thống kê địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    from datetime import datetime, timedelta

    from django.utils import timezone

    from apps.checkin.models import Checkin

    # Thống kê check-in
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_checkins = Checkin.objects.filter(
        location=location, created_at__date=today
    ).count()

    week_checkins = Checkin.objects.filter(
        location=location, created_at__date__gte=week_start
    ).count()

    month_checkins = Checkin.objects.filter(
        location=location, created_at__date__gte=month_start
    ).count()

    total_checkins = Checkin.objects.filter(location=location).count()

    context = {
        "location": location,
        "today_checkins": today_checkins,
        "week_checkins": week_checkins,
        "month_checkins": month_checkins,
        "total_checkins": total_checkins,
    }
    return render(request, "location/statistics.html", context)


# API Views
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def location_list_api(request):
    """API danh sách địa điểm"""
    if request.method == "GET":
        locations = Location.objects.filter(is_active=True)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def location_detail_api(request, location_id):
    """API chi tiết địa điểm"""
    location = get_object_or_404(Location, id=location_id)

    if request.method == "GET":
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = LocationSerializer(location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == "DELETE":
        location.delete()
        return Response(status=204)
