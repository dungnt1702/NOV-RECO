from django.shortcuts import render
from django.urls import path

from .views import (
    personal_avatar_upload_view,
    personal_checkin_history_view,
    personal_password_change_view,
    personal_profile_edit_view,
    personal_profile_view,
)

app_name = "personal"


def avatar_test_view(request):
    """Test avatar upload functionality"""
    return render(request, "personal/avatar_test.html")


urlpatterns = [
    # Personal profile management
    path("profile/", personal_profile_view, name="profile"),
    path("edit/", personal_profile_edit_view, name="edit"),
    path("change-password/", personal_password_change_view, name="change_password"),
    path("avatar-upload/", personal_avatar_upload_view, name="avatar_upload"),
    path("avatar-test/", avatar_test_view, name="avatar_test"),
    path("checkin-history/", personal_checkin_history_view, name="checkin_history"),
]
