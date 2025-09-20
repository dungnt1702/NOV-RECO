from django.urls import path
from .views import (
    dashboard,
    checkin_page,
    AreaListView,
    checkin_submit_view,
    checkin_list_api,
    user_info_api,
    checkin_list_view,
    users_api,
    checkin_success_view,
    user_history_view,
    quick_checkin_view,
    user_history_api,
    last_checkin_api,
    areas_api,
    area_detail_api,
    area_management,
    update_checkins_areas_api,
)

urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    # Check-in
    path("", checkin_page, name="checkin_page"),
    path("areas-list/", AreaListView.as_view(), name="areas_list"),
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
    # Area Management (Admin/Manager only)
    path("areas/", areas_api, name="areas_api"),
    path("areas/<int:area_id>/", area_detail_api, name="area_detail_api"),
    path("area-management/", area_management, name="area_management"),
    path(
        "update-checkins-areas/",
        update_checkins_areas_api,
        name="update_checkins_areas",
    ),
]
