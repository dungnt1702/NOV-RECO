from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Add common security headers to all responses for basic hardening."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Transport/Isolation
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        # Allow camera/geolocation on same-origin (needed for Chrome's Permissions Policy)
        response["Permissions-Policy"] = (
            "geolocation=(self), camera=(self), microphone=(self)"
        )

        # Keep HSTS disabled in local to avoid issues on http
        # If behind https/prod, set via environment/webserver.

        # Basic CSP that allows same-origin resources and static
        # Allow local assets by default, plus specific trusted CDNs we currently use
        # TODO: vendor CDN assets into static/ and then tighten CSP back to 'self' only
        # Force a permissive CSP to allow external CDN (Leaflet) and fonts in all modes
        response["Content-Security-Policy"] = (
            "default-src * data: blob: 'unsafe-inline' 'unsafe-eval';"
        )

        return response
