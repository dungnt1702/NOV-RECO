from django.urls import path
from .views import checkin_page, LocationListView, CheckinCreateView

urlpatterns = [
    path("", checkin_page, name="checkin_page"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("submit/", CheckinCreateView.as_view(), name="checkin_submit"),
]
