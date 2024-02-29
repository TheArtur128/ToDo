from os import getenv
from secrets import token_urlsafe

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv("SECRET_KEY", default=token_urlsafe(64))

IS_DEV = bool(int(getenv("IS_DEV", default="1")))

DEBUG = IS_DEV

HOST = getenv("HOST", default="http://localhost:8000")
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [HOST]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    "apps.access",
    "apps.confirmation",
    "apps.shared",
    "apps.tasks",
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
        "DIRS": [BASE_DIR / "apps/access/presentation/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        }
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("POSRTGES_NAME", default="todo"),
        "USER": getenv("POSRTGES_USER", default="todo"),
        "PASSWORD": getenv("POSRTGES_PASSWORD", default="todo"),
        "HOST": getenv("POSRTGES_HOST", default="localhost"),
        "PORT": getenv("POSRTGES_PORT", default="5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    }
]

AUTH_USER_MODEL = "shared.User"

LOGIN_URL = "/sign-in"

URL_TO_REDIRECT_NON_ANONYMOUS = '/'


LANGUAGE_CODE = "en-us"

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


EMAIL_HOST = getenv("EMAIL_HOST", default=None)
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD", default=None)
EMAIL_PORT = int(getenv("EMAIL_PORT", default=0))
EMAIL_USE_TLS = bool(int(getenv("EMAIL_USE_TLS", default=False)))
EMAIL_USE_SSL = bool(int(getenv("EMAIL_USE_SSL", default=False)))

DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL", default=None)
EMAIL_ADMIN = getenv("EMAIL_ADMIN", default=DEFAULT_FROM_EMAIL)


CONFIRMATION_SESSION_CODE_LENGTH = 64
CONFIRMATION_ACTIVATION_CODE_LENGTH = 8
CONFIRMATION_ACTIVITY_MINUTES = 8

REDIS_PASSWORD = getenv("REDIS_PASSWORD", default="todo")
REDIS_SOCKET = getenv("REDIS_SOCKET", default="localhost:6379")

REDIS_BASIC_LOCATION = f"redis://{REDIS_SOCKET}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_BASIC_LOCATION}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_BASIC_LOCATION}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
        }
    },
    "confirmation": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_BASIC_LOCATION}/2",
        "TIMEOUT": 60 * CONFIRMATION_ACTIVITY_MINUTES,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
        }
    },
    "accounts": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_BASIC_LOCATION}/3",
        "TIMEOUT": 60 * CONFIRMATION_ACTIVITY_MINUTES,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
        }
    },
    "passwords": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_BASIC_LOCATION}/4",
        "TIMEOUT": 60 * CONFIRMATION_ACTIVITY_MINUTES,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": REDIS_PASSWORD,
        }
    },
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"
