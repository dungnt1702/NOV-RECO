from django.urls import path
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
    user_list_api,
    user_create_api,
    user_update_api,
)

app_name = "users"

urlpatterns = [
    # User management views
    path("list/", user_list_view, name="list"),
    path("create/", user_create_view, name="create"),
    path("update/<int:user_id>/", user_update_view, name="update"),
    path("detail/<int:user_id>/", user_detail_view, name="detail"),
    path("delete/<int:user_id>/", user_delete_view, name="delete"),
    path("toggle/<int:user_id>/", user_toggle_active_view, name="toggle"),
    
    # Department management views
    path("departments/", department_list_view, name="department_list"),
    path("departments/create/", department_create_view, name="department_create"),
    path("departments/update/<int:dept_id>/", department_update_view, name="department_update"),
    path("departments/delete/<int:dept_id>/", department_delete_view, name="department_delete"),
    
    # APIs
    path("api/", user_list_api, name="list_api"),
    path("api/create/", user_create_api, name="create_api"),
    path("api/<int:user_id>/update/", user_update_api, name="update_api"),
]
