# -*- coding: utf-8 -*-
"""
Urls for signup.
"""
from django.conf.urls import patterns, url, include
from .views import TicketCreateView, TicketPayView, TicketReceiptView, TicketStartView


urlpatterns = patterns(
    '',
    url(r'^$', TicketStartView.as_view(), name='ticket-start'),
    url(r'^order/(?P<ticket_type_slug>[-\w]+)/$', TicketCreateView.as_view(), name='ticket-booking'),
    url(r'^(?P<hashid>\w+)/pay/$', TicketPayView.as_view(), name='ticket-payment'),
    url(r'^(?P<hashid>\w+)/receipt/$', TicketReceiptView.as_view(), name='ticket-receipt'),
)
