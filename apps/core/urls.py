from django.urls import path

from .views import offline_view

app_name = "core"

urlpatterns = [
    path("offline/", offline_view, name="offline"),
]
