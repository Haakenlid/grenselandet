""" Settings for local development """

from .dev import *

# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'localemail@localhost'

# TOOLBAR CONFIGURATION
INTERNAL_IPS = ['127.0.0.1', ]
