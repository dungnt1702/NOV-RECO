import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Environment Configuration
ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")

# Security
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "rest_framework",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # Local apps
    "apps.common",
    "apps.checkin",
    "apps.location",
    "apps.employee", 
    "apps.dashboard",
    "apps.personal",
    "apps.users",
    "apps.automation_test",
    "apps.absence",
    "apps.notifications",
    "apps.module_settings",
]

MIDDLEWARE = [
    "apps.common.middleware.SecurityHeadersMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "apps.checkin.middleware.FaviconMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "apps.module_settings.middleware.ModulePermissionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.checkin.context_processors.current_year",
                # "apps.module_settings.decorators.module_enabled_context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database Configuration
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3")

if DATABASE_ENGINE == "django.db.backends.postgresql":
    # PostgreSQL configuration for production
    DATABASES = {
        "default": {
            "ENGINE": DATABASE_ENGINE,
            "NAME": os.environ.get("DATABASE_NAME", "nov_reco_checkin_prod"),
            "USER": os.environ.get("DATABASE_USER", "nov_reco_user"),
            "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
            "HOST": os.environ.get("DATABASE_HOST", "localhost"),
            "PORT": os.environ.get("DATABASE_PORT", "5432"),
        }
    }
else:
    # SQLite configuration (default for local development)
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "data/db.sqlite3")
    if not DATABASE_NAME.startswith("/"):
        DATABASE_NAME = BASE_DIR / DATABASE_NAME
    
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DATABASE_NAME,
        }
    }

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# Internationalization
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "vi")
TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Ho_Chi_Minh")
USE_I18N = True
USE_TZ = True

# Static Files Configuration
STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT = os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles")
if isinstance(STATIC_ROOT, str) and not STATIC_ROOT.startswith("/"):
    STATIC_ROOT = BASE_DIR / STATIC_ROOT

STATICFILES_DIRS = (
    [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
)

# Media Files Configuration
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", BASE_DIR / "media")
if isinstance(MEDIA_ROOT, str) and not MEDIA_ROOT.startswith("/"):
    MEDIA_ROOT = BASE_DIR / MEDIA_ROOT

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-allauth
SITE_ID = int(os.environ.get("SITE_ID", "1"))
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 3

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["openid", "email", "profile"],
        "AUTH_PARAMS": {"access_type": "online"},
        # You can optionally pin hosted domain
        # "HOSTED_DOMAIN": "yourcompany.com",
        # Put Client ID/Secret in Admin (recommended). Or uncomment APP below:
        # "APP": {"client_id": "xxx", "secret": "yyy", "key": ""},
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Email Configuration
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT") or "587")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "0") == "1"

# Logging Configuration
# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if ENVIRONMENT in ["production", "test"] else ['console'],
            'level': os.environ.get("LOG_LEVEL", "INFO" if ENVIRONMENT in ["production", "test"] else "DEBUG"),
        },
        'apps.checkin': {
            'handlers': ['console', 'file'] if ENVIRONMENT in ["production", "test"] else ['console'],
            'level': os.environ.get("LOG_LEVEL", "INFO" if ENVIRONMENT in ["production", "test"] else "DEBUG"),
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console', 'file'] if ENVIRONMENT in ["production", "test"] else ['console'],
            'level': os.environ.get("LOG_LEVEL", "INFO" if ENVIRONMENT in ["production", "test"] else "DEBUG"),
            'propagate': False,
        },
    },
}
