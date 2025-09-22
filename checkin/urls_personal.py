from django.urls import path
from .views_personal import (
    personal_profile_view,
    personal_edit_view,
    personal_change_password_view,
    personal_avatar_upload_view,
)

app_name = "personal"

urlpatterns = [
    # Personal profile management
    path("profile/", personal_profile_view, name="profile"),
    path("edit/", personal_edit_view, name="edit"),
    path("change-password/", personal_change_password_view, name="change_password"),
    path("avatar-upload/", personal_avatar_upload_view, name="avatar_upload"),
]
