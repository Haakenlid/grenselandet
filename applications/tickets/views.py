# -*- coding: utf-8 -*-
"""
Views for the participant registration and payment for the event.
"""
# from annoying.functions import get_object_or_None
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
# from django.template import loader, Context
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView

from django.contrib.sites.models import get_current_site

from django.conf import settings
# from django.contrib import messages

from .models import Ticket, TicketType
from applications.conventions.models import Convention
from .forms import TicketForm


class DateCheckMixin(object):

    """ Checks that signup is not closed. """

    closed_url = 'signup-closed'

    def date_overdue(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse(self.closed_url))

    def dispatch(self, request, *args, **kwargs):
        if timezone.now() > self.overdue:
            return self.date_overdue(request, *args, **kwargs)
        return super(DateCheckMixin, self).dispatch(request, *args, **kwargs)


class ClosedView(TemplateView):

    """ Main view when ticket sales is closed. """
    template_name = 'signup-closed.html'


class TicketStartView(TemplateView):
    template_name = 'ticket-start.html'
    convention = Convention.objects.exclude(end_time__lt=timezone.now()).order_by('start_time').first()

    def get_context_data(self, **kwargs):
        """Adds sold_out to context"""
        context = super().get_context_data(**kwargs)
        ticket_types = TicketType.objects.exclude(status=TicketType.SECRET).filter(ticket_pool__convention=self.convention)
        context.update(ticket_types=ticket_types)
        context.update(convention=self.convention)
        return context


class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket-create.html'
    next_url_label = 'ticket-payment'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('ticket_type_slug')
        self.ticket_type = get_object_or_404(
            TicketType.objects.exclude(status=TicketType.COMING_SOON).exclude(status=TicketType.SOLD_OUT),
            slug=slug,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Adds sold_out to context"""
        context = super().get_context_data(**kwargs)
        context.update(ticket_type=self.ticket_type)
        context.update(convention=self.ticket_type.ticket_pool.convention)
        return context

    def form_valid(self, form):
        self.object = form.save(ticket_type=self.ticket_type)
        return HttpResponseRedirect(self.get_success_url())


class TicketMixin:
    model = Ticket
    context_object_name = 'ticket'
    slug_field = 'hashid'
    slug_url_kwarg = 'hashid'

    def get_success_url(self):
        """ Send user to next part of the process. """
        return reverse(
            self.next_url_label,
            kwargs={'hashid': self.object.hashid},
        )




class TicketPayView(TicketMixin, DetailView):

    """ Participant pay their ticket. """
    template_name = 'ticket-pay.html'

    def dispatch(self, request, *args, **kwargs):
        self.ticket = get_object_or_404(
            Ticket,
            hashid=self.kwargs.get('hashid')
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Adds sold_out to context"""
        context = super().get_context_data(**kwargs)
        context.update(ticket_type=self.ticket.ticket_type)
        context.update(ticket=self.ticket)
        context.update(ticket_data=(
            ('ticket-id', self.ticket.hashid, ),
            ('event', self.ticket.convention, ),
            ('ticket type', self.ticket.ticket_type.name, ),
            ('price', self.ticket.ticket_type.get_price_display(), ),
            ('ticket holder', self.ticket.get_full_name(), ),
            ('date of birth', self.ticket.date_of_birth, ),
            ('email', self.ticket.email, ),
            ('address', self.ticket.address, ),
            ('country', self.ticket.country.name, ),
            ), )
        return context

    # def form_valid(self, form):
    #     # self.object = form.save(ticket_type=self.ticket_type)
    #     return HttpResponseRedirect(self.get_success_url())

class TicketReceiptView(TicketPayView):

    """ Show receipt data for ticket """
    # template_name = 'ticket-pay.html'