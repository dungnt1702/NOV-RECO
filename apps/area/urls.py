from django.urls import path
from .views import (
    area_list_view,
    area_create_view,
    area_update_view,
    area_detail_view,
    area_delete_view,
    area_toggle_active_view,
    area_checkin_history_view,
    area_statistics_view,
    area_list_api,
    area_detail_api,
)

app_name = "area"

urlpatterns = [
    # Area management views
    path("list/", area_list_view, name="list"),
    path("create/", area_create_view, name="create"),
    path("update/<int:area_id>/", area_update_view, name="update"),
    path("detail/<int:area_id>/", area_detail_view, name="detail"),
    path("delete/<int:area_id>/", area_delete_view, name="delete"),
    path("toggle/<int:area_id>/", area_toggle_active_view, name="toggle"),
    path("history/<int:area_id>/", area_checkin_history_view, name="history"),
    path("statistics/<int:area_id>/", area_statistics_view, name="statistics"),
    
    # APIs
    path("api/", area_list_api, name="api"),
    path("api/<int:area_id>/", area_detail_api, name="detail_api"),
]
