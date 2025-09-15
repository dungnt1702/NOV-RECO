from django.urls import path
from .views import (
    dashboard, checkin_page, LocationListView, CheckinCreateView, 
    checkin_list_api, user_management
)

urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    
    # Check-in
    path("", checkin_page, name="checkin_page"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("submit/", CheckinCreateView.as_view(), name="checkin_submit"),
    path("list/", checkin_list_api, name="checkin_list"),
    
    # User Management (Admin only)
    path("users/", user_management, name="user_management"),
]
