from django.urls import path
from .views import (
    location_list_view,
    location_create_view,
    location_update_view,
    location_detail_view,
    location_delete_view,
    location_toggle_active_view,
    location_checkin_history_view,
    location_statistics_view,
    location_list_api,
    location_detail_api,
)

app_name = "location"

urlpatterns = [
    # Location management views
    path("list/", location_list_view, name="list"),
    path("create/", location_create_view, name="create"),
    path("update/<int:location_id>/", location_update_view, name="update"),
    path("detail/<int:location_id>/", location_detail_view, name="detail"),
    path("delete/<int:location_id>/", location_delete_view, name="delete"),
    path("toggle/<int:location_id>/", location_toggle_active_view, name="toggle"),
    path("history/<int:location_id>/", location_checkin_history_view, name="history"),
    path("statistics/<int:location_id>/", location_statistics_view, name="statistics"),
    
    # APIs
    path("api/", location_list_api, name="api"),
    path("api/<int:location_id>/", location_detail_api, name="detail_api"),
]
