# -*- coding: utf-8 -*-
"""
Url config for skeleton project
"""
from django.contrib import admin
from django.conf.urls import patterns, include, url
from autocomplete_light import urls as autocomplete_light_urls
from core.views import RobotsTxtView, HumansTxtView

urlpatterns = patterns(
    '',
    # your urls here
)

urlpatterns += patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', RobotsTxtView.as_view(), name='robots.txt'),
    url(r'^humans.txt$', HumansTxtView.as_view(), name='humans.txt'),
    url(r'^autocomplete/', include(autocomplete_light_urls)),
)
