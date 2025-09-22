from django.urls import path
from .views import (
    dashboard_main_view,
    dashboard_personal_view,
    dashboard_secretary_view,
    dashboard_hr_view,
    dashboard_manager_view,
)

app_name = "dashboard"

urlpatterns = [
    # Main dashboard router
    path("", dashboard_main_view, name="main"),
    
    # Specific dashboards
    path("personal/", dashboard_personal_view, name="personal"),
    path("secretary/", dashboard_secretary_view, name="secretary"),
    path("hr/", dashboard_hr_view, name="hr"),
    path("manager/", dashboard_manager_view, name="manager"),
]
