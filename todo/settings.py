from os import getenv

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = getenv("BASE_URL")

SECRET_KEY = getenv("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "access",
    "tasks",
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

ROOT_URLCONF = "todo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages"],
            "libraries": {
                "common_tags": "core.templatetags.common_tags"}
        }
    }
]

WSGI_APPLICATION = "todo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3"
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator")
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator")
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator")
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator")
    }
]

AUTH_USER_MODEL = "tasks.User"

LOGIN_URL = "/sign-in"

URL_TO_REDIRECT_NON_ANONYMOUS = '/'


LANGUAGE_CODE = "en-us"

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(getenv("EMAIL_PORT"))
EMAIL_USE_TLS = bool(int(getenv("EMAIL_USE_TLS", default=False)))
EMAIL_USE_SSL = bool(int(getenv("EMAIL_USE_SSL", default=False)))

DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
EMAIL_ADMIN = getenv("EMAIL_ADMIN", default=DEFAULT_FROM_EMAIL)


PORT_AUTHENTICATION_TOKEN_LENGTH = 64
PORT_PASSWORD_LENGTH = 8
PORT_ACTIVITY_MINUTES = 5
PORTS_CACHE_LOCATION = "ports"

PORTS = {
    "registration": {"FOR_AUTHORIZED": False, "HANDLER": "access:registrate"},
    "authorization": {"FOR_AUTHORIZED": False, "HANDLER": "access:authorize"},
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'db': '0'
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'db': '1',
        }
    },
    "ports": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
        "TIMEOUT": 60 * PORT_ACTIVITY_MINUTES,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'db': '2'
        }
    },
    "emails-to-confirm": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
        "TIMEOUT": 60 * PORT_ACTIVITY_MINUTES,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'db': '3',
        }
    },
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
