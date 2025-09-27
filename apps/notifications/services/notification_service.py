import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from ..models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service gửi thông báo nâng cao"""

    @staticmethod
    def send_approval_notification(absence_request, approver):
        """Gửi thông báo cần phê duyệt"""
        # Tạo notification
        notification = Notification.objects.create(
            user=approver,
            title="Đơn vắng mặt cần phê duyệt",
            message=f"Đơn vắng mặt của {absence_request.user.get_full_name()} cần phê duyệt",
            type="approval_required",
            is_important=True,
            data={
                "absence_request_id": absence_request.id,
                "requester_name": absence_request.user.get_full_name(),
                "absence_type": absence_request.absence_type.name,
                "start_date": absence_request.start_date.isoformat(),
                "end_date": absence_request.end_date.isoformat(),
                "approval_level": absence_request.approval_level,
                "department": (
                    absence_request.user.department.full_name
                    if absence_request.user.department
                    else "N/A"
                ),
            },
            related_object_id=absence_request.id,
            related_object_type="AbsenceRequest",
        )

        # Gửi email
        NotificationService._send_email_notification(notification)

        # Gửi push notification (nếu có mobile app)
        NotificationService._send_push_notification(notification)

        return notification

    @staticmethod
    def send_reminder_notification(absence_request, approver, reminder_count):
        """Gửi thông báo nhắc nhở"""
        notification = Notification.objects.create(
            user=approver,
            title=f"Nhắc nhở phê duyệt (lần {reminder_count})",
            message=f"Đơn vắng mặt của {absence_request.user.get_full_name()} vẫn chưa được phê duyệt",
            type="reminder",
            is_important=True,
            data={
                "absence_request_id": absence_request.id,
                "reminder_count": reminder_count,
                "requester_name": absence_request.user.get_full_name(),
                "start_date": absence_request.start_date.isoformat(),
                "end_date": absence_request.end_date.isoformat(),
            },
        )

        NotificationService._send_email_notification(notification)
        return notification

    @staticmethod
    def send_completion_notification(absence_request):
        """Gửi thông báo hoàn thành"""
        notification = Notification.objects.create(
            user=absence_request.user,
            title="Đơn vắng mặt đã được duyệt",
            message=f"Đơn vắng mặt của bạn đã được phê duyệt",
            type="approval_completed",
            data={
                "absence_request_id": absence_request.id,
                "absence_type": absence_request.absence_type.name,
                "start_date": absence_request.start_date.isoformat(),
                "end_date": absence_request.end_date.isoformat(),
                "approved_by": (
                    absence_request.approved_by.get_full_name()
                    if absence_request.approved_by
                    else "Hệ thống"
                ),
            },
        )

        NotificationService._send_email_notification(notification)
        return notification

    @staticmethod
    def send_rejection_notification(absence_request):
        """Gửi thông báo từ chối"""
        notification = Notification.objects.create(
            user=absence_request.user,
            title="Đơn vắng mặt bị từ chối",
            message=f"Đơn vắng mặt của bạn đã bị từ chối: {absence_request.rejection_reason}",
            type="approval_rejected",
            data={
                "absence_request_id": absence_request.id,
                "absence_type": absence_request.absence_type.name,
                "start_date": absence_request.start_date.isoformat(),
                "end_date": absence_request.end_date.isoformat(),
                "rejection_reason": absence_request.rejection_reason,
                "rejected_by": (
                    absence_request.approved_by.get_full_name()
                    if absence_request.approved_by
                    else "Hệ thống"
                ),
            },
        )

        NotificationService._send_email_notification(notification)
        return notification

    @staticmethod
    def send_system_notification(user, title, message, is_important=False, data=None):
        """Gửi thông báo hệ thống"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type="system",
            is_important=is_important,
            data=data or {},
        )

        NotificationService._send_email_notification(notification)
        return notification

    @staticmethod
    def send_checkin_notification(user, title, message, data=None):
        """Gửi thông báo chấm công"""
        notification = Notification.objects.create(
            user=user, title=title, message=message, type="checkin", data=data or {}
        )

        return notification

    @staticmethod
    def _send_email_notification(notification):
        """Gửi email notification"""
        try:
            subject = f"[NOV-RECO] {notification.title}"
            message = f"""
            {notification.message}
            
            Thời gian: {notification.created_at.strftime('%d/%m/%Y %H:%M')}
            
            Vui lòng truy cập hệ thống để xem chi tiết.
            """

            send_mail(
                subject, message, settings.DEFAULT_FROM_EMAIL, [notification.user.email]
            )
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    @staticmethod
    def _send_push_notification(notification):
        """Gửi push notification (cho mobile app)"""
        # Implement push notification logic here
        # Có thể sử dụng Firebase, OneSignal, etc.
        pass

    @staticmethod
    def mark_notification_read(notification_id, user):
        """Đánh dấu thông báo đã đọc"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_notifications_read(user):
        """Đánh dấu tất cả thông báo đã đọc"""
        Notification.objects.filter(user=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

    @staticmethod
    def get_user_notifications(user, notification_type=None, limit=20):
        """Lấy danh sách thông báo của user"""
        notifications = Notification.objects.filter(user=user)

        if notification_type:
            notifications = notifications.filter(type=notification_type)

        return notifications.order_by("-created_at")[:limit]

    @staticmethod
    def get_unread_count(user):
        """Lấy số thông báo chưa đọc"""
        return Notification.get_unread_count(user)

    @staticmethod
    def cleanup_expired_notifications():
        """Dọn dẹp thông báo hết hạn"""
        expired_notifications = Notification.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired_notifications.count()
        expired_notifications.delete()
        return count
