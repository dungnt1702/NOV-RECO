from django.urls import path

from . import views

app_name = "module_settings"

urlpatterns = [
    path("", views.module_settings_list, name="list"),
    path("toggle/<str:module_name>/", views.toggle_module, name="toggle"),
    path("api/status/", views.module_status_api, name="api_status"),
]
