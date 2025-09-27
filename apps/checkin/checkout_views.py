from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from apps.location.models import Location
from apps.module_settings.decorators import require_module_enabled
from apps.users.models import User
from apps.users.permissions import permission_required

from .models import Checkin, Checkout
from .serializers import CheckoutListSerializer
from .utils import find_best_location_for_checkin


@login_required
def checkout_action_view(request):
    """Trang checkout chính - hiển thị checkin hiện tại để checkout"""
    # Lấy checkin_id từ URL parameter nếu có
    checkin_id = request.GET.get("checkin_id")

    if checkin_id:
        # Nếu có checkin_id, lấy checkin cụ thể
        try:
            latest_checkin = get_object_or_404(
                Checkin, id=checkin_id, user=request.user
            )
            # Kiểm tra xem checkin đã có checkout chưa
            if Checkout.objects.filter(checkin=latest_checkin).exists():
                latest_checkin = None  # Đã checkout rồi
        except:
            latest_checkin = None
    else:
        # Lấy checkin gần nhất của user hiện tại chưa có checkout
        latest_checkin = (
            Checkin.objects.filter(user=request.user)
            .exclude(checkouts__isnull=False)  # Loại bỏ checkin đã có checkout
            .order_by("-created_at")
            .first()
        )

    context = {
        "latest_checkin": latest_checkin,
    }
    return render(request, "checkin/checkout.html", context)


@login_required
@require_http_methods(["POST"])
def checkout_submit_view(request):
    """Xử lý submit checkout"""
    try:
        # Lấy checkin_id từ form
        checkin_id = request.POST.get("checkin_id")
        if not checkin_id:
            return JsonResponse(
                {"success": False, "error": "Không tìm thấy thông tin checkin"},
                status=400,
            )

        # Lấy checkin object
        checkin = get_object_or_404(Checkin, id=checkin_id, user=request.user)

        # Kiểm tra xem checkin đã có checkout chưa
        if Checkout.objects.filter(checkin=checkin).exists():
            return JsonResponse(
                {"success": False, "error": "Checkin này đã có checkout rồi"},
                status=400,
            )

        # Lấy dữ liệu từ form
        lat = float(request.POST.get("lat", 0))
        lng = float(request.POST.get("lng", 0))
        note = request.POST.get("note", "")
        address = request.POST.get("address", "")  # Địa chỉ từ reverse geocoding

        # Lấy ảnh
        photo = request.FILES.get("photo")
        if not photo:
            return JsonResponse(
                {"success": False, "error": "Vui lòng chụp ảnh"}, status=400
            )

        # Tự động tìm địa điểm gần nhất dựa trên tọa độ
        location_name, distance = find_best_location_for_checkin(lat, lng)

        # Lấy location object nếu có (để lưu vào DB cho backward compatibility)
        location = None
        if location_name != "Không xác định":
            try:
                location = Location.objects.filter(
                    name=location_name, is_active=True
                ).first()
            except Location.DoesNotExist:
                pass

        # Tạo checkout
        checkout = Checkout.objects.create(
            user=request.user,
            checkin=checkin,
            lat=lat,
            lng=lng,
            address=address,
            photo=photo,
            note=note,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # Tính khoảng cách
        if location:
            checkout.distance_m = distance
            checkout.save(update_fields=["distance_m"])

        # Chuẩn bị dữ liệu trả về
        success_data = {
            "checkout_id": checkout.id,
            "checkin_id": checkin.id,
            "location_name": location_name,
            "distance": distance,
            "created_at": checkout.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "message": "Checkout thành công!",
        }

        return JsonResponse({"success": True, "data": success_data})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"Lỗi: {str(e)}"}, status=500)


@login_required
@require_module_enabled("checkin")
def checkout_success_view(request, checkout_id):
    """Trang thành công sau khi checkout"""
    try:
        checkout = get_object_or_404(
            Checkout.objects.select_related("user", "user__department", "checkin"),
            id=checkout_id,
            user=request.user,
        )
        success_data = {
            "user_name": checkout.user.get_display_name(),
            "user_email": checkout.user.email,
            "user_department": (
                checkout.user.department.name if checkout.user.department else "N/A"
            ),
            "user_employee_id": checkout.user.username,
            "location_name": checkout.get_location_name(),
            "coordinates": (f"{checkout.lat:.6f}, {checkout.lng:.6f}"),
            "address": checkout.address or "Không xác định",
            "created_at": checkout.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "note": checkout.note or "",
            "photo_url": (checkout.photo.url if checkout.photo else None),
            "checkin_id": checkout.checkin.id,
            "checkout_id": checkout.id,
            "message": "Checkout thành công!",
        }

        context = {
            "success_data": success_data,
        }
        return render(request, "checkin/checkout_success.html", context)

    except Exception as e:
        return render(
            request, "checkin/checkout_success.html", {"error": f"Lỗi: {str(e)}"}
        )


@login_required
@require_module_enabled("checkin")
def checkout_detail_view(request, checkin_id):
    """Chi tiết checkout của một checkin cụ thể"""
    try:
        # Lấy checkin và checkout tương ứng
        checkin = get_object_or_404(
            Checkin.objects.select_related("user", "user__department"),
            id=checkin_id,
            user=request.user,
        )

        checkout = get_object_or_404(
            Checkout.objects.select_related("user", "user__department"),
            checkin=checkin,
            user=request.user,
        )

        context = {
            "checkin": checkin,
            "checkout": checkout,
            "title": "Chi tiết Check-out",
        }
        return render(request, "checkin/checkout_detail.html", context)

    except Exception as e:
        return render(
            request, "checkin/checkout_detail.html", {"error": f"Lỗi: {str(e)}"}
        )


@login_required
def checkout_history_view(request):
    """Lịch sử checkout"""
    checkouts = Checkout.objects.filter(user=request.user).order_by("-created_at")

    # Pagination
    paginator = Paginator(checkouts, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "checkouts": page_obj,
    }
    return render(request, "checkin/checkout_history.html", context)


@permission_required("checkin.can_view_all_checkouts")
def checkout_list_view(request):
    """Danh sách checkout cho quản lý"""
    checkouts = Checkout.objects.select_related("user", "checkin").order_by(
        "-created_at"
    )

    # Filtering
    search = request.GET.get("search", "")
    user_id = request.GET.get("user_id", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if search:
        checkouts = checkouts.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(note__icontains=search)
        )

    if user_id:
        checkouts = checkouts.filter(user_id=user_id)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(checkouts, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Lấy danh sách users để filter
    users = User.objects.filter(is_active=True).order_by("first_name", "last_name")

    context = {
        "checkouts": page_obj,
        "users": users,
        "search": search,
        "user_id": user_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    return render(request, "checkin/checkout_list.html", context)


# API Views
@login_required
def checkout_list_api(request):
    """API danh sách checkout"""
    checkouts = Checkout.objects.select_related("user", "checkin").order_by(
        "-created_at"
    )

    # Filtering
    search = request.GET.get("search", "")
    user_id = request.GET.get("user_id", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if search:
        checkouts = checkouts.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(note__icontains=search)
        )

    if user_id:
        checkouts = checkouts.filter(user_id=user_id)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Pagination
    per_page = int(request.GET.get("per_page", 50))
    page = int(request.GET.get("page", 1))

    paginator = Paginator(checkouts, per_page)
    page_obj = paginator.get_page(page)

    serializer = CheckoutListSerializer(page_obj.object_list, many=True)

    return JsonResponse(
        {
            "checkouts": serializer.data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
    )


@login_required
def checkout_history_api(request):
    """API lịch sử checkout cho user hiện tại"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Chỉ lấy checkout của user hiện tại
    checkouts = Checkout.objects.filter(user=request.user).order_by("-created_at")

    # Filtering
    search = request.GET.get("search", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if search:
        checkouts = checkouts.filter(
            Q(note__icontains=search) | Q(checkin__note__icontains=search)
        )

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            checkouts = checkouts.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Pagination
    per_page = int(request.GET.get("per_page", 20))
    page = int(request.GET.get("page", 1))

    paginator = Paginator(checkouts, per_page)
    page_obj = paginator.get_page(page)

    serializer = CheckoutListSerializer(page_obj.object_list, many=True)

    return JsonResponse(
        {
            "checkouts": serializer.data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
    )
