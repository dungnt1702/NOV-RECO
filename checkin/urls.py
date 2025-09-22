from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Modular URL includes - hierarchical structure
    path("checkin/", include("checkin.urls_checkin")),
    path("area/", include("checkin.urls_area")),
    path("employee/", include("checkin.urls_employee")),
    path("personal/", include("checkin.urls_personal")),
    path("dashboard/", include("checkin.urls_dashboard")),
    
    # Legacy redirects for backward compatibility
    path("action/", lambda request: redirect("checkin:action"), name="checkin_page"),
    path("area-management/", lambda request: redirect("area:list"), name="area_management"),
    path("area-list/", lambda request: redirect("area:list"), name="area_list"),
    path("area-form/", lambda request: redirect("area:form"), name="area_form"),
    path("area-form/<int:area_id>/", lambda request, area_id: redirect("area:edit", area_id=area_id), name="area_edit"),
]
