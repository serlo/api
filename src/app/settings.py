DEBUG = True
SECRET_KEY = "u052ixbr8xoew*b3q*ozn4dg(ud#x!kuz-wfa=7%m49wj_ud7o"
ALLOWED_HOSTS = ["localhost", "api"]

# Application definition
INSTALLED_APPS = [
    "corsheaders",
    "graphene_django",
    "serlo_org.apps.SerloOrgConfig",
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]
ROOT_URLCONF = "app.urls"

WSGI_APPLICATION = "app.wsgi.application"
GRAPHENE = {"SCHEMA": "app.schema.schema"}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "secret",
        "HOST": "db",
        "PORT": "",
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
USE_I18N = False
USE_L10N = False
USE_TZ = True

# CORS
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:4000",
]
