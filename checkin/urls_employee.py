from django.urls import path
from .views_employee import (
    employee_list_view,
    employee_form_view,
    employee_detail_view,
    employee_delete_view,
    employee_list_api,
    employee_create_api,
    employee_detail_api,
    employee_update_api,
    employee_delete_api,
)

app_name = "employee"

urlpatterns = [
    # Employee management views
    path("list/", employee_list_view, name="list"),
    path("form/", employee_form_view, name="form"),
    path("form/<int:employee_id>/", employee_form_view, name="edit"),
    path("detail/<int:employee_id>/", employee_detail_view, name="detail"),
    path("delete/<int:employee_id>/", employee_delete_view, name="delete"),
    
    # APIs
    path("api/", employee_list_api, name="list_api"),
    path("api/create/", employee_create_api, name="create_api"),
    path("api/<int:employee_id>/", employee_detail_api, name="detail_api"),
    path("api/<int:employee_id>/update/", employee_update_api, name="update_api"),
    path("api/<int:employee_id>/delete/", employee_delete_api, name="delete_api"),
]
