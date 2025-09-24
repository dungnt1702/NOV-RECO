from django.urls import path
from django.shortcuts import redirect, render
from .views import (
    user_list_view,
    user_create_view,
    user_update_view,
    user_detail_view,
    user_delete_view,
    user_toggle_active_view,
    department_list_view,
    department_create_view,
    department_update_view,
    department_delete_view,
    office_list_view,
    office_create_view,
    office_update_view,
    office_delete_view,
    user_list_api,
    user_create_api,
    user_update_api,
    department_list_api,
    debug_current_user,
)

def debug_user_view(request):
    """Debug user information"""
    return render(request, 'debug_user.html')

app_name = "users"

urlpatterns = [
    # Index -> users list
    path("", lambda request: redirect("users:list"), name="index"),
    # Debug view
    path("debug/", debug_current_user, name="debug"),
    # User management views
    path("list/", user_list_view, name="list"),
    path("list/office_id/<int:office_id>/", user_list_view, name="list_by_office"),
    path("create/", user_create_view, name="create"),
    path("update/<int:user_id>/", user_update_view, name="update"),
    path("detail/<int:user_id>/", user_detail_view, name="detail"),
    path("delete/<int:user_id>/", user_delete_view, name="delete"),
    path("toggle/<int:user_id>/", user_toggle_active_view, name="toggle"),
    
    # Office management views
    path("offices/", office_list_view, name="office_list"),
    path("offices/create/", office_create_view, name="office_create"),
    path("offices/update/<int:office_id>/", office_update_view, name="office_update"),
    path("offices/delete/<int:office_id>/", office_delete_view, name="office_delete"),
    
    # Department management views
    path("departments/", department_list_view, name="department_list"),
    path("departments/office_id/<int:office_id>/", department_list_view, name="department_list_by_office"),
    path("departments/create/", department_create_view, name="department_create"),
    path("departments/update/<int:dept_id>/", department_update_view, name="department_update"),
    path("departments/delete/<int:dept_id>/", department_delete_view, name="department_delete"),
    
    # APIs
    path("api/", user_list_api, name="list_api"),
    path("api/create/", user_create_api, name="create_api"),
    path("api/<int:user_id>/update/", user_update_api, name="update_api"),
    path("api/departments/", department_list_api, name="department_list_api"),
]
