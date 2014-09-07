# -*- coding: utf-8 -*-
"""
Django settings for universitas_no project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: path.join(SITE_ROOT, ...)
import os
from os.path import dirname, join, normpath
# import django.conf.global_settings as DEFAULT_SETTINGS


def env(keyname):
    """ shortcut for getting environmental variables """
    return os.environ('DJANGO_{keyname}'.format(keyname=keyname.upper().replace(' ', '_')))

# CORE CONFIG
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
SECRET_KEY = env('SECRET_KEY')
SITE_URL = env('SITE_URL')

# These values are set in the virtualenv postactivate bash file to keep sensitive information out of GitHub

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# CUSTOM APPS
INSTALLED_APPS = (
    'core',
    'functional_tests',
)

# THIRD PARTY APPS
INSTALLED_APPS = (
    'autocomplete_light',
    'django_extensions',
    'sorl.thumbnail',
) + INSTALLED_APPS

# CORE APPS
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
) + INSTALLED_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',  # Set to empty string for default.
    },
}

# SORL THUMBNAILS
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.convert_engine.Engine'

# CACHE
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 0,
            # 'PASSWORD': 'yadayada',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        },
    },
}

# When using unix domain sockets with Redis
# Note: ``LOCATION`` needs to be the same as the ``unixsocket`` setting
# in your redis.conf
# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': '/path/to/socket/file',
#         'OPTIONS': {
#             'DB': 1,
#             'PASSWORD': 'yadayada',
#             'PARSER_CLASS': 'redis.connection.HiredisParser'
#         },
#     },


# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory containing all
# files under version control, including all django files.
BASE_DIR = env('SOURCE_FOLDER')

# Absolute filesystem path to the top-level project folder containing
# static folder, log folder, virtualenv and configs not under version
# control.
PROJECT_ROOT_FOLDER = dirname(BASE_DIR)

# This is where static files are collected by django and served by the webserver.
STATIC_ROOT = normpath(join(PROJECT_ROOT_FOLDER, 'static'))
STATIC_URL = '/static/'

# User uploaded files.
MEDIA_ROOT = normpath(join(PROJECT_ROOT_FOLDER, 'static/media'))
MEDIA_URL = '/media/'

STATICFILES_DIRS = (normpath(join(BASE_DIR, 'assets')), )  # Extra path to look for javascript, css and so on.
FIXTURE_DIRS = (normpath(join(BASE_DIR, 'fixtures')), )   # Project wide fixtures, not connected to individual apps.
TEMPLATE_DIRS = (normpath(join(BASE_DIR, 'templates')), )  # Project wide templates
LOG_FOLDER = normpath(join(PROJECT_ROOT_FOLDER, 'logs'))  # Where to save log messages. Not a core django configuration.

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

# INTERNATIONALIZATION
LANGUAGE_CODE = 'nb_NO'
TIME_ZONE = 'Europe/Oslo'
USE_I18N = True  # Internationalisation (string translation)
USE_L10N = True  # Localisation (numbers and stuff)
USE_TZ = True    # Use timezone
LOCALE_PATHS = (normpath(join(BASE_DIR, 'translation')), )  # Django puts generated translation files here.

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'stream_to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': normpath(join(LOG_FOLDER, 'django-debug.log')),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'stream_to_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug': {
            'handlers': ['stream_to_console', 'file', ],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
