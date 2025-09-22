from django.urls import path
from .views_checkin import (
    checkin_action_view,
    checkin_success_view,
    checkin_history_view,
    checkin_list_view,
    checkin_submit_view,
    checkin_list_api,
    user_history_api,
    last_checkin_api,
    user_info_api,
)

app_name = "checkin"

urlpatterns = [
    # Check-in actions
    path("action/", checkin_action_view, name="action"),
    path("submit/", checkin_submit_view, name="submit"),
    path("success/<int:checkin_id>/", checkin_success_view, name="success"),
    
    # History and lists
    path("history/", checkin_history_view, name="history"),
    path("list/", checkin_list_view, name="list"),
    
    # APIs
    path("api/list/", checkin_list_api, name="list_api"),
    path("api/history/", user_history_api, name="history_api"),
    path("api/last-checkin/", last_checkin_api, name="last_checkin_api"),
    path("api/user-info/", user_info_api, name="user_info_api"),
]
