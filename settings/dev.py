"""Development settings and globals."""

from .base import *

# DEBUG CONFIGURATION
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'core.dev_urls'

# APPS AND MIDDLEWARE USED ONLY IN DEVELOPMENT
INSTALLED_APPS += ['debug_toolbar', ]
MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = env_var('DEBUG_TOOLBAR_INTERNAL_IPS').split(' ')

PAYMILL_PUBLIC_KEY = '80711414564043477fab642827961bd5'