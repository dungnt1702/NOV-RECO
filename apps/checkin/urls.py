from django.urls import path, include
from . import urls_checkin

app_name = "checkin"

urlpatterns = [
    # Include checkin URLs at root level
    path("", include(urls_checkin)),
]
