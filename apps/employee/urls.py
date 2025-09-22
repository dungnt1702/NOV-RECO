from django.urls import path
from .views import (
    employee_list_view,
    employee_create_view,
    employee_update_view,
    employee_detail_view,
    employee_delete_view,
    employee_toggle_active_view,
    employee_checkin_history_view,
    employee_statistics_view,
    employee_list_api,
    employee_create_api,
    employee_update_api,
)

app_name = "employee"

urlpatterns = [
    # Employee management views
    path("list/", employee_list_view, name="list"),
    path("create/", employee_create_view, name="create"),
    path("update/<int:employee_id>/", employee_update_view, name="update"),
    path("detail/<int:employee_id>/", employee_detail_view, name="detail"),
    path("delete/<int:employee_id>/", employee_delete_view, name="delete"),
    path("toggle/<int:employee_id>/", employee_toggle_active_view, name="toggle"),
    path("history/<int:employee_id>/", employee_checkin_history_view, name="history"),
    path("statistics/<int:employee_id>/", employee_statistics_view, name="statistics"),
    
    # APIs
    path("api/", employee_list_api, name="list_api"),
    path("api/create/", employee_create_api, name="create_api"),
    path("api/<int:employee_id>/update/", employee_update_api, name="update_api"),
]
