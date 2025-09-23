from django.urls import path
from .views import (
    checkin_action_view,
    checkin_submit_view,
    checkin_success_view,
    checkin_history_view,
    checkin_list_view,
    checkin_list_api,
    checkin_history_api,
)

app_name = "checkin"

urlpatterns = [
    # Check-in views
    path("action/", checkin_action_view, name="action"),
    path("submit/", checkin_submit_view, name="submit"),
    path("success/", checkin_success_view, name="success"),
    path("history/", checkin_history_view, name="history"),
    path("list/", checkin_list_view, name="list"),

    # APIs
    path("api/", checkin_list_api, name="list_api"),
    path("api/history/", checkin_history_api, name="history_api"),
]
