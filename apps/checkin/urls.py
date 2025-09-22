from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Modular URL includes - hierarchical structure
    path("checkin/", include("apps.checkin.urls_checkin")),
    path("area/", include("apps.area.urls")),
    path("employee/", include("apps.employee.urls")),
    path("personal/", include("apps.personal.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    
    # Legacy redirects for backward compatibility
    path("action/", lambda request: redirect("checkin:action"), name="checkin_page"),
    path("area-management/", lambda request: redirect("area:list"), name="area_management"),
    path("area-list/", lambda request: redirect("area:list"), name="area_list"),
    path("area-form/", lambda request: redirect("area:form"), name="area_form"),
    path("area-form/<int:area_id>/", lambda request, area_id: redirect("area:edit", area_id=area_id), name="area_edit"),
]
