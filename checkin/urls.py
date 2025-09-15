from django.urls import path
from .views import (
    dashboard, checkin_page, LocationListView, CheckinCreateView,
    checkin_list_api, user_management, user_info_api, checkin_list_view, users_api
)

urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),

    # Check-in
    path("", checkin_page, name="checkin_page"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("submit/", CheckinCreateView.as_view(), name="checkin_submit"),
    path("list/", checkin_list_api, name="checkin_list"),
    path("list-view/", checkin_list_view, name="checkin_list_view"),
    path("user-info/", user_info_api, name="user_info"),
    path("users-api/", users_api, name="users_api"),

    # User Management (Admin only)
    path("users/", user_management, name="user_management"),
]
