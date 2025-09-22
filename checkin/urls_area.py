from django.urls import path
from .views_area import (
    area_list_view,
    area_form_view,
    areas_api,
    area_detail_api,
    update_checkins_areas_api,
)

app_name = "area"

urlpatterns = [
    # Area management views
    path("list/", area_list_view, name="list"),
    path("form/", area_form_view, name="form"),
    path("form/<int:area_id>/", area_form_view, name="edit"),
    
    # APIs
    path("api/", areas_api, name="api"),
    path("api/<int:area_id>/", area_detail_api, name="detail_api"),
    path("api/update-checkins/", update_checkins_areas_api, name="update_checkins"),
]
