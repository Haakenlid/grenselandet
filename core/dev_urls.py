# -*- coding: utf-8 -*-
"""
Url config for skeleton project during development
"""
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from debug_toolbar import urls as debug_toolbar_urls

from .urls import urlpatterns

# django debug toolbar
urlpatterns += patterns('', url(r'^__debug__/', include(debug_toolbar_urls)), )
# serve media files from development server
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
