# -*- coding: utf-8 -*-
"""
Django settings for skeleton project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
from django.conf import global_settings


def env_var(keyname):
    """ shortcut for getting environmental variables """
    # To avoid commiting passwords and usernames to git and GitHub,
    # these settings are saved as environmental variables in a file called postactivate.
    # Postactivate is sourced when the virtual environment is activated.
    return os.environ.get('DJANGO_{keyname}'.format(keyname=keyname.upper().replace(' ', '_')))


def join_path(*paths):
    """ shortcut for joining paths. cross os compatible """
    return os.path.normpath(os.path.join(*paths))


# CORE CONFIG
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
SECRET_KEY = env_var('SECRET_KEY')
SITE_URL = env_var('SITE_URL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [env_var('SITE_URL'), ]
ADMINS = (('Håken Lid', 'haakenlid@gmail.com'),)

# PAYMILL API KEYS
PAYMILL_PUBLIC_KEY = env_var('PAYMILL_PUBLIC_KEY')
PAYMILL_PRIVATE_KEY = env_var('PAYMILL_PRIVATE_KEY')

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env_var('GMAIL_USER')
EMAIL_HOST_PASSWORD = env_var('GMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# CUSTOM APPS
INSTALLED_APPS = [
    'core',
    'functional_tests',
    'applications.conventions',
    'applications.mail',
    'applications.tickets',
]

# THIRD PARTY APPS
INSTALLED_APPS = [
    'autocomplete_light',
    'django_extensions',
    'sorl.thumbnail',
    'sekizai',
    'compressor',
    'widget_tweaks',
] + INSTALLED_APPS

# CORE APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + INSTALLED_APPS

# MIDDLEWARE
MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.request',
)
# POSTGRESQL DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env_var('DB_NAME'),
        'USER': env_var('DB_USER'),
        'PASSWORD': env_var('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',  # Set to empty string for default.
    },
}

# SORL THUMBNAILS
# Redis used as key-value store
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
# ImageMagick ( or Ubuntu's graphicsmagick-imagemagick-compat )
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.convert_engine.Engine'


# REDIS CACHE
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 0,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        },
    },
}

# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory containing all
# files under version control, including django files.
BASE_DIR = env_var('SOURCE_FOLDER')

# Absolute filesystem path to the top-level project folder containing
# static folder, log folder, virtualenv and configs not under version control.
PROJECT_DIR = join_path(BASE_DIR, '..')

# This is where static files are collected to by django and served by the webserver.
STATIC_ROOT = join_path(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

# User uploaded files location.
MEDIA_ROOT = join_path(PROJECT_DIR, 'static', 'media')
MEDIA_URL = '/media/'

# Extra path to collect static assest such as javascript and css
STATICFILES_DIRS = [join_path(BASE_DIR, 'assets'), ]
# Project wide fixtures to be loaded into database.
FIXTURE_DIRS = [join_path(BASE_DIR, 'fixtures'), ]
# Project wide django template files
TEMPLATE_DIRS = [join_path(BASE_DIR, 'templates'), ]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'compressor.finders.CompressorFinder',
]

# INTERNATIONALIZATION AND TRANSLATION
LANGUAGE_CODE = 'en'  # English
TIME_ZONE = 'Europe/Oslo'
USE_I18N = True  # Internationalisation (string translation)
USE_L10N = True  # Localisation (numbers and stuff)
USE_TZ = True    # Use timezone
LOCALE_PATHS = [join_path(BASE_DIR, 'translation'), ]  # Django puts generated translation files here.

# LOGGING
DEBUG_LOG_FILE = join_path(PROJECT_DIR, 'logs', 'django-debug.log')

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
        'write_to_logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILE,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'stream_to_console', ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug': {
            'handlers': ['stream_to_console', 'write_to_logfile', ],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
