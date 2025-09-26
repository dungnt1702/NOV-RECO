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
from .checkout_views import (
    checkout_action_view,
    checkout_submit_view,
    checkout_success_view,
    checkout_history_view,
    checkout_list_view,
    checkout_list_api,
    checkout_history_api,
    checkout_detail_view,
)

# app_name = "checkin"  # Commented out to avoid namespace conflict

urlpatterns = [
    # Check-in views
    path("action/", checkin_action_view, name="action"),
    path("submit/", checkin_submit_view, name="submit"),
    path(
        "success/checkin_id/<int:checkin_id>/",
        checkin_success_view,
        name="success",
    ),
    path("history/", checkin_history_view, name="history"),
    path("list/", checkin_list_view, name="list"),

    # APIs
    path("api/", checkin_list_api, name="list_api"),
    path("api/history/", checkin_history_api, name="history_api"),
    path("api/user-info/", checkin_user_info_api, name="user_info_api"),

    # Check-out views
    path("checkout/", checkout_action_view, name="checkout"),
    path("checkout/submit/", checkout_submit_view, name="checkout_submit"),
    path(
        "checkout/success/checkout_id/<int:checkout_id>/",
        checkout_success_view,
        name="checkout_success",
    ),
    path("checkout/history/", checkout_history_view, name="checkout_history"),
    path("checkout/list/", checkout_list_view, name="checkout_list"),
    path(
        "checkout/detail/<int:checkin_id>/",
        checkout_detail_view,
        name="checkout_detail",
    ),

    # Check-out APIs
    path("checkout/api/", checkout_list_api, name="checkout_list_api"),
    path(
        "checkout/api/history/",
        checkout_history_api,
        name="checkout_history_api"
    ),
]
