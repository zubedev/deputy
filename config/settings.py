from pathlib import Path
from typing import Any

import django_stubs_ext
from decouple import Csv, config
from dj_database_url import parse as parse_db_url

django_stubs_ext.monkeypatch()

# https://docs.djangoproject.com/en/dev/ref/settings/

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# SECURITY WARNING: keep the secret key used in production secret! Set in .env file or in the environment variables
SECRET_KEY: str = config("SECRET_KEY", cast=str)
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = config("DEBUG", cast=bool, default=False)

# App definition # --------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/applications/
DJANGO_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS: list[str] = [
    # https://www.django-rest-framework.org/
    "rest_framework",
    # https://github.com/adamchainz/django-cors-headers
    "corsheaders",
    # https://github.com/carltongibson/django-filter
    "django_filters",
    # https://drf-spectacular.readthedocs.io/en/latest/index.html
    "drf_spectacular",
]
LOCAL_APPS: list[str] = [
    "core",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS: list[str] = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF: str = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES: list[dict[str, Any]] = [
    {
        # https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(BASE_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION: str = "config.wsgi.application"

# Database # --------------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES: dict[str, Any] = {
    "default": config("DATABASE_URL", cast=parse_db_url, default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
# https://docs.djangoproject.com/en/dev/topics/db/transactions/#module-django.db.transaction
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# Authentication # --------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS: list[str] = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "core.User"

# SECURITY # --------------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", cast=Csv(), default="")
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# Internationalization # --------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE: str = config("LANGUAGE_CODE", cast=str, default="en-us")
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE: str = config("TIME_ZONE", cast=str, default="UTC")
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N: bool = config("USE_I18N", cast=bool, default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ: bool = config("USE_TZ", cast=bool, default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# Static # ----------------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL: str = config("STATIC_URL", cast=str, default="static/")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT: str = config("STATIC_ROOT", cast=str, default=BASE_DIR / "staticfiles")

# Media # ------------------------------------------------------------------------------------------------------------ #

# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL: str = config("MEDIA_URL", cast=str, default="media/")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT: str = config("MEDIA_ROOT", cast=str, default=BASE_DIR / "media")

# REST Framework # --------------------------------------------------------------------------------------------------- #

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    # API Policy https://www.django-rest-framework.org/api-guide/settings/#api-policy-settings
    # https://www.django-rest-framework.org/api-guide/authentication/
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    # https://www.django-rest-framework.org/api-guide/parsers/
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    # https://www.django-rest-framework.org/api-guide/permissions/
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # https://www.django-rest-framework.org/api-guide/renderers/
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # https://www.django-rest-framework.org/api-guide/schemas/
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # https://www.django-rest-framework.org/api-guide/throttling/
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "10/second", "user": "100/second"},
    # Generic View https://www.django-rest-framework.org/api-guide/settings/#generic-view-settings
    # https://www.django-rest-framework.org/api-guide/filtering/
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # https://www.django-rest-framework.org/api-guide/pagination/
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    # Testing https://www.django-rest-framework.org/api-guide/settings/#test-settings
    # https://www.django-rest-framework.org/api-guide/testing/
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    # Miscellaneous https://www.django-rest-framework.org/api-guide/settings/#miscellaneous-settings
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}
if DEBUG:  # enable Browsable API only in DEBUG mode
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append("rest_framework.renderers.BrowsableAPIRenderer")  # type: ignore

# DRF Spectacular # -------------------------------------------------------------------------------------------------- #

# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "deputy API",
    "DESCRIPTION": "Documentation of API endpoints of deputy",
    "VERSION": "0.1.0",
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelsExpandDepth": 5,  # default 1 (-1 to hide models)
        "defaultModelExpandDepth": 5,  # default 1 (expansion depth)
    },
}

# Logging # ---------------------------------------------------------------------------------------------------------- #

# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# https://docs.djangoproject.com/en/dev/topics/logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
