from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("accounts/", include("allauth.urls")),  # Google Sign-In routes
        path(
            "",
            TemplateView.as_view(template_name="home.html"),
            name="home",
        ),
        path(
            "", include(("apps.checkin.urls", "checkin"), namespace="checkin")
        ),  # All modules at root level with namespace
        path("area/", include("apps.area.urls")),  # Area management
        path("users/", include("apps.users.urls")),  # User management
        path(
            "automation-test/", include("apps.automation_test.urls")
        ),  # Automation test
        path("dashboard/", include("apps.dashboard.urls")),  # Dashboard
        path("personal/", include("apps.personal.urls")),  # Personal profile
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
