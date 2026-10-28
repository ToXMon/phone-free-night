import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "events",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Local default is SQLite so the scaffold runs with no setup.
# Production: DATABASE_URL wins (Neon, Fly, Render all provide one), then
# POSTGRES_* / PG* (Neon's console shows PG*), then SQLite.
# Neon notes, from Neon's own Django guide:
# - Use the -pooler endpoint for a web app, so PgBouncer pools connections.
# - sslmode=require on any *.neon.tech host.
# - DISABLE_SERVER_SIDE_CURSORS and CONN_HEALTH_CHECKS keep pooled
#   connections from going stale after Neon scales to zero.
def _postgres_config(name, user, password, host, port):
    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
    }
    if host.endswith("neon.tech"):
        config["OPTIONS"] = {"sslmode": "require"}
        config["DISABLE_SERVER_SIDE_CURSORS"] = True
        config["CONN_HEALTH_CHECKS"] = True
    return config


def _database_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    config = _postgres_config(
        parsed.path.lstrip("/"),
        parsed.username or "",
        parsed.password or "",
        parsed.hostname or "",
        str(parsed.port or 5432),
    )
    if "sslmode" in query:
        config.setdefault("OPTIONS", {})["sslmode"] = query["sslmode"][0]
    return config


if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": _database_from_url(os.environ["DATABASE_URL"])}
elif os.environ.get("POSTGRES_DB") or os.environ.get("PGHOST"):
    DATABASES = {
        "default": _postgres_config(
            os.environ.get("POSTGRES_DB") or os.environ.get("PGDATABASE", ""),
            os.environ.get("POSTGRES_USER") or os.environ.get("PGUSER", "postgres"),
            os.environ.get("POSTGRES_PASSWORD") or os.environ.get("PGPASSWORD", ""),
            os.environ.get("POSTGRES_HOST") or os.environ.get("PGHOST", "localhost"),
            os.environ.get("POSTGRES_PORT") or os.environ.get("PGPORT", "5432"),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "event-list"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
