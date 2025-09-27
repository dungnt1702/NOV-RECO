from .base import *

# Local development settings
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

# Relaxed security for local development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development-specific settings
if DEBUG:
    # Remove Django's security middleware to avoid CSP conflicts
    MIDDLEWARE = [
        mw for mw in MIDDLEWARE if mw != "django.middleware.security.SecurityMiddleware"
    ]

    # Move our CSP middleware to the end to override any other CSP settings
    MIDDLEWARE = [
        mw
        for mw in MIDDLEWARE
        if mw != "apps.common.middleware.SecurityHeadersMiddleware"
    ]
    MIDDLEWARE.append("apps.common.middleware.SecurityHeadersMiddleware")

    # Debug toolbar is already configured in base.py
    INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]
