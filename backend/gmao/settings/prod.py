"""
Production settings — MySQL from environment variables.
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Allow the Netlify frontend URL (e.g. https://my-gmao.netlify.app)
_extra_cors = os.environ.get("CORS_ALLOWED_ORIGINS", "")
if _extra_cors:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _extra_cors.split(",") if o.strip()]

# ─── MySQL (REQ-12 — InnoDB ACID) ─────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET storage_engine=InnoDB",
        },
    }
}

# Security hardening
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
