from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path(
        "",
        TemplateView.as_view(template_name="home.html"),
        name="home",
    ),
    # Mount checkin app under /checkin/ with namespace
    path("checkin/", include(("apps.checkin.urls", "checkin"), namespace="checkin")),
    path("area/", include("apps.area.urls")),
    path("employee/", include("apps.employee.urls")),
    path("personal/", include("apps.personal.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("users/", include("apps.users.urls")),
    path("automation-test/", include("apps.automation_test.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
