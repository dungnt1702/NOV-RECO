from .base import *

# Test settings
DEBUG = False
TESTING = True

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable debug toolbar in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware
]

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable logging in tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Cache backend for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Password hashers for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Media files for tests
MEDIA_ROOT = BASE_DIR / "test_media"
MEDIA_URL = "/test_media/"

# Static files for tests
STATIC_ROOT = BASE_DIR / "test_static"
STATIC_URL = "/test_static/"

# Disable module settings middleware for tests
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE if "module_settings" not in middleware
]
