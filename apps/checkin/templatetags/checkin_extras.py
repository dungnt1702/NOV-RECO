from datetime import datetime, timedelta

from django import template
from django.utils import timezone

import pytz

register = template.Library()


@register.filter
def work_duration(checkout_time, checkin_time):
    """
    Tính thời gian làm việc giữa checkin và checkout
    Trả về format: HH:MM:SS hoặc X giờ Y phút
    """
    if not checkout_time or not checkin_time:
        return "N/A"

    # Tính khoảng thời gian
    duration = checkout_time - checkin_time

    # Chuyển đổi thành giây
    total_seconds = int(duration.total_seconds())

    # Tính giờ, phút, giây
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Format theo kiểu Việt Nam
    if hours > 0:
        if minutes > 0:
            return f"{hours} giờ {minutes} phút"
        else:
            return f"{hours} giờ"
    elif minutes > 0:
        if seconds > 0:
            return f"{minutes} phút {seconds} giây"
        else:
            return f"{minutes} phút"
    else:
        return f"{seconds} giây"


@register.filter
def work_duration_detailed(checkout_time, checkin_time):
    """
    Tính thời gian làm việc với format chi tiết HH:MM:SS
    """
    if not checkout_time or not checkin_time:
        return "N/A"

    duration = checkout_time - checkin_time
    total_seconds = int(duration.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@register.filter
def utc_time(datetime_obj):
    """
    Hiển thị thời gian UTC thực sự (không bị convert timezone)
    """
    if not datetime_obj:
        return "N/A"

    # Chuyển về UTC nếu có timezone info
    if timezone.is_aware(datetime_obj):
        utc_time = datetime_obj.astimezone(pytz.UTC)
    else:
        utc_time = datetime_obj

    return utc_time.strftime("%d/%m/%Y %H:%M:%S UTC")
