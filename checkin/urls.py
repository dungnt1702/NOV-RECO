from django.urls import path
from .views import (
    dashboard,
    checkin_page,
    LocationListView,
    checkin_submit_view,
    checkin_list_api,
    user_management,
    user_info_api,
    checkin_list_view,
    users_api,
    checkin_success_view,
    user_history_view,
    quick_checkin_view,
    user_history_api,
    last_checkin_api,
)

urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    # Check-in
    path("", checkin_page, name="checkin_page"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("submit/", checkin_submit_view, name="checkin_submit"),
    path("list/", checkin_list_api, name="checkin_list"),
    path("list-view/", checkin_list_view, name="checkin_list_view"),
    path("success/", checkin_success_view, name="checkin_success"),
    path("history/", user_history_view, name="user_history"),
    path("quick/", quick_checkin_view, name="quick_checkin"),
    path("user-info/", user_info_api, name="user_info"),
    path("users-api/", users_api, name="users_api"),
    path("user-history/", user_history_api, name="user_history_api"),
    path("last-checkin/", last_checkin_api, name="last_checkin_api"),
    # User Management (Admin only)
    path("users/", user_management, name="user_management"),
]
