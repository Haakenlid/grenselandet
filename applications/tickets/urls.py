# -*- coding: utf-8 -*-
"""
Urls for signup.
"""
from django.conf.urls import patterns, url, include
from .views import MainView, TicketCreateView, TicketPayView, TicketPrioritiseView, TicketReceiptView, PrioritiesListView, priorities_csv, ClosedView


urlpatterns = patterns(
    '',
    url(r'^$', MainView.as_view(), name='signup-root'),
    url(r'^register/$', TicketCreateView.as_view(), name='ticket-create'),
    url(r'^games/(?P<uuid>[0-9a-z]+)/$', TicketPrioritiseView.as_view(), name='ticket-prioritise'),
    url(r'^pay/(?P<uuid>[0-9a-z]+)/$', TicketPayView.as_view(), name='ticket-pay'),
    url(r'^receipt/(?P<uuid>[0-9a-z]+)/$', TicketReceiptView.as_view(), name='ticket-receipt'),
    url(r'^priorities-list/$', PrioritiesListView.as_view(), name='priorities-list'),
    url(r'^priorities\.csv$', priorities_csv, name='priorities-csv'),
    url(r'^closed/$', ClosedView.as_view(), name='signup-closed'),


)

# Paypal

urlpatterns += patterns(
    '',
    url(r'^paypal/notify-ipn/',
        include('paypal.standard.ipn.urls'),),
    url(r'^paypal/return/$',
        'signup.views.paypal_return', name='payment-return'),
    url(r'^paypal/cancel/$',
        'signup.views.paypal_cancel', name='payment-cancel'),
)
