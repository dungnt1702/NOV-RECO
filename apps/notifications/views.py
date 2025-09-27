from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .services import NotificationService


@login_required
def notification_list_view(request):
    """Trang danh sách thông báo"""
    notifications = Notification.objects.filter(user=request.user)

    # Filter theo type
    notification_type = request.GET.get("type")
    if notification_type:
        notifications = notifications.filter(type=notification_type)

    # Pagination
    paginator = Paginator(notifications.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Thống kê
    stats = {
        "total": notifications.count(),
        "unread": notifications.filter(is_read=False).count(),
        "by_type": notifications.values("type").annotate(count=Count("id")),
    }

    return render(
        request,
        "notifications/list.html",
        {"page_obj": page_obj, "stats": stats, "current_type": notification_type},
    )


@login_required
@require_http_methods(["POST"])
def mark_notification_read_view(request, notification_id):
    """Đánh dấu thông báo đã đọc"""
    success = NotificationService.mark_notification_read(notification_id, request.user)

    if success:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "Notification not found"}, status=404)


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read_view(request):
    """Đánh dấu tất cả thông báo đã đọc"""
    NotificationService.mark_all_notifications_read(request.user)
    return JsonResponse({"success": True})


# API Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_api(request):
    """API lấy thông báo"""
    notifications = Notification.objects.filter(user=request.user)

    # Filter
    notification_type = request.GET.get("type")
    if notification_type:
        notifications = notifications.filter(type=notification_type)

    # Pagination
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))

    start = (page - 1) * page_size
    end = start + page_size

    notifications_page = notifications[start:end]

    data = {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "type_display": n.type_display,
                "is_read": n.is_read,
                "is_important": n.is_important,
                "created_at": n.created_at.isoformat(),
                "data": n.data,
            }
            for n in notifications_page
        ],
        "total": notifications.count(),
        "unread_count": notifications.filter(is_read=False).count(),
        "has_next": end < notifications.count(),
    }

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read_api(request, notification_id):
    """API đánh dấu thông báo đã đọc"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()

        return Response({"success": True})
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read_api(request):
    """API đánh dấu tất cả thông báo đã đọc"""
    NotificationService.mark_all_notifications_read(request.user)
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count_api(request):
    """API lấy số thông báo chưa đọc"""
    count = NotificationService.get_unread_count(request.user)
    return Response({"unread_count": count})
