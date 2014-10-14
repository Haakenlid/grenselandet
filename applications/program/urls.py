# -*- coding: utf-8 -*-
"""
Urls for program.
"""
from django.conf.urls import patterns, url
from .views import schedule, hashid_schedule, sessionlist, reshuffle, public_list, participantlist, blekke, program_oppslag


urlpatterns = patterns(
    '',
    url(r'^$', schedule, name='program-schedule'),
    url(r'^sessions/$', sessionlist, name='program-sessionlist'),
    url(r'^(?P<hashid>\w+)/$', hashid_schedule, name='hashid-schedule'),
    url(r'^participants/$', participantlist, name='program-participants'),
    url(r'^reshuffle/$', reshuffle, name='program-reshuffle'),
    url(r'^games/$', public_list, name='program-public-list'),
    url(r'^blekke/$', blekke, name='program-blekke'),
    url(r'^oppslag/$', program_oppslag, name='program-oppslag'),
)
