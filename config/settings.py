from secrets import token_urlsafe

from pathlib import Path
from typenv import Env


env = Env()
env.read_env()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY", default=token_urlsafe(64))

IS_DEV = env.bool("IS_DEV", default=True)

DEBUG = IS_DEV

PROTOCOL = env.str("PROTOCOL", default="http://")
DOMAIN = env.str("DOMAIN", default="localhost")

HOST = f"{PROTOCOL}{DOMAIN}"

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

    "rest_framework",

    "apps.access",
    "apps.confirmation",
    "apps.map",
    "apps.profile_",
    "apps.shared",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.shared.middleware.default_header_settings_middleware",
]

ROOT_URLCONF = "config.urls"

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
                "django.contrib.messages.context_processors.messages",
            ],
        }
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSRTGES_NAME", default="todo"),
        "USER": env.str("POSRTGES_USER", default="todo"),
        "PASSWORD": env.str("POSRTGES_PASSWORD", default="todo"),
        "HOST": env.str("POSRTGES_HOST", default="localhost"),
        "PORT": env.str("POSRTGES_PORT", default="5432"),
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

AUTH_USER_MODEL = "access.User"

LOGIN_URL = "/sign-in"

URL_TO_REDIRECT_NON_ANONYMOUS = '/'


LANGUAGE_CODE = "en-us"

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


EMAIL_HOST = env.str("EMAIL_HOST", default=None)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default=None)
EMAIL_PORT = env.int("EMAIL_PORT", default=0)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=None)
EMAIL_ADMIN = env.str("EMAIL_ADMIN", default=DEFAULT_FROM_EMAIL)


CONFIRMATION_SESSION_CODE_LENGTH = 64
CONFIRMATION_ACTIVATION_CODE_LENGTH = 8
CONFIRMATION_ACTIVITY_MINUTES = 8

FILE_CONFIRMATION_ONLY = env.bool("FILE_CONFIRMATION_ONLY", default=False)

REDIS_PASSWORD = env.str("REDIS_PASSWORD", default="todo")
REDIS_SOCKET = env.str("REDIS_SOCKET", default="localhost:6379")

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


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.PageNumberPagination'
    ),
    'PAGE_SIZE': 20,
}


DEFAULT_HEADERS = {"HTTP_HOST": DOMAIN}
