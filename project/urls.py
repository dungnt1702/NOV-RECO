from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
        path("", include("checkin.urls")),  # All modules at root level
        path("users/", include("users.urls")),  # User management
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
