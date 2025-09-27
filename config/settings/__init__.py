import os

from .base import *

# Load environment-specific settings
ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")

if ENVIRONMENT == "production":
    from .production import *
elif ENVIRONMENT == "test":
    from .local import *  # Use local settings for test environment
else:
    from .local import *
