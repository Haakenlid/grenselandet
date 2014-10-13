# -*- coding: utf-8 -*-
"""
Url config for skeleton project
"""
from django.contrib import admin
from django.conf.urls import patterns, include, url
from autocomplete_light import urls as autocomplete_light_urls
from applications.tickets.urls import urlpatterns as ticket_urls
from applications.program.urls import urlpatterns as program_urls
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from core.views import RobotsTxtView, HumansTxtView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = patterns(
    '',
    # your urls here
)

urlpatterns += patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(ticket_urls)),
    url(r'^program/', include(program_urls)),
    url(r'^robots.txt$', RobotsTxtView.as_view(), name='robots.txt'),
    url(r'^humans.txt$', HumansTxtView.as_view(), name='humans.txt'),
    url(r'^autocomplete/', include(autocomplete_light_urls)),
)

dajaxice_autodiscover()
# Dajaxice
urlpatterns += patterns(
    '',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

# staticfiles
urlpatterns += staticfiles_urlpatterns()
