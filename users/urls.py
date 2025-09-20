from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Web views
    path("", views.user_list_view, name="user_list"),
    path("create/", views.user_create_view, name="user_create"),
    path("<int:user_id>/update/", views.user_update_view, name="user_update"),
    path("<int:user_id>/delete/", views.user_delete_view, name="user_delete"),
    path("departments/", views.department_list_view, name="department_list"),
    # API endpoints
    path("api/", views.user_list_api, name="user_list_api"),
    path("api/create/", views.user_create_api, name="user_create_api"),
    path("api/<int:user_id>/", views.user_detail_api, name="user_detail_api"),
]
