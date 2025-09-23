from django.urls import path, include
from django.shortcuts import redirect
from . import urls_checkin

app_name = "checkin"

urlpatterns = [
    # Index -> checkin action
    path("", lambda request: redirect("checkin:action"), name="index"),
    # Include checkin URLs at root level
    path("", include(urls_checkin)),
]
