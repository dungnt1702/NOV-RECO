from django.urls import path
from .views import (
    checkin_action_view,
    checkin_submit_view,
    checkin_success_view,
    checkin_history_view,
    checkin_list_view,
    checkin_list_api,
    checkin_history_api,
    checkin_user_info_api,
)

# app_name = "checkin"  # Commented out to avoid namespace conflict

urlpatterns = [
    # Check-in views
    path("action/", checkin_action_view, name="action"),
    path("submit/", checkin_submit_view, name="submit"),
    path("success/", checkin_success_view, name="success"),
    path(
        "success/checkin_id/<int:checkin_id>/",
        checkin_success_view,
        name="success_by_id",
    ),
    path("history/", checkin_history_view, name="history"),
    path("list/", checkin_list_view, name="list"),

    # APIs
    path("api/", checkin_list_api, name="list_api"),
    path("api/history/", checkin_history_api, name="history_api"),
    path("api/user-info/", checkin_user_info_api, name="user_info_api"),
]
