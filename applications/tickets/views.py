# -*- coding: utf-8 -*-
"""
Views for the participant registration and payment for the event.
"""
# from annoying.functions import get_object_or_None
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template import loader, Context
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
from signup.models import *
from signup.forms import *
from dateutil.parser import parse
from datetime import datetime

# do not edit! added by PythonBreakpoints
from pdb import set_trace as _breakpoint

DATE_CLOSED = parse('2014-07-17 10:00')


class DateCheckMixin(object):

    """ Checks that signup is not closed. """

    closed_url = 'signup-closed'
    def date_overdue(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse(self.closed_url))

    def dispatch(self, request, *args, **kwargs):
        if datetime.now() > DATE_CLOSED:
            return self.date_overdue(request, *args, **kwargs)
        return super(DateCheckMixin, self).dispatch(request, *args, **kwargs)


class ClosedView(TemplateView):

    """ Main view when ticket sales is closed. """
    template_name = 'signup-closed.html'


class MainView(DateCheckMixin, TemplateView):
    template_name = 'signup-root.html'

    def get_context_data(self, **kwargs):
        """Adds sold_out to context"""
        context = super(MainView, self).get_context_data(**kwargs)
        context['sold_out'] = Ticket.objects.sold_out()
        return context


class PrioritiesListView(TemplateView):

    """ Show list of games and participants' priorities. """

    template_name = 'priorities-list.html'

    def get_context_data(self, **kwargs):
        context = super(PrioritiesListView, self).get_context_data(**kwargs)
        priorities = ActivityPriority.objects.filter(
            activity__published=True,
            ticket__activated=True,
            priority__gt=1,
        ).order_by(
            'activity',
            '-priority',
        ).select_related(
            'ticket',
            'activity',
        )
        priorities_by_player = priorities.order_by('ticket', '-priority')
        context['priorities'] = priorities
        context['priorities_by_player'] = priorities_by_player
        return context


class TicketMixin:
    model = Ticket
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    context_object_name = 'ticket'

    def get_success_url(self):
        """ Send user to next part of the process. """
        return reverse(
            self.next_url_label,
            kwargs={'uuid': self.object.uuid},)


class TicketCreateView(DateCheckMixin, TicketMixin, CreateView,):
    template_name = 'ticket-create.html'
    form_class = TicketForm
    next_url_label = 'ticket-prioritise'


class TicketPrioritiseView(DateCheckMixin, TicketMixin, UpdateView, ):
    template_name = 'ticket-prioritise.html'
    form_class = PriorityFormSet
    # inline_model = ActivityPriority
    next_url_label = 'ticket-pay'

    def get_object(self, *args, **kwargs):
        print('get_object',)
        """Return Ticket object based on uuid"""
        # TODO session based version
        ticket = super(TicketPrioritiseView, self).get_object(*args, **kwargs)
        ticket.createPriorities()
        return ticket

    def form_valid(self, form):
        print('form_valid',)
        """ Valid """
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return form_invalid(self, form)


class TicketReceiptView(TicketMixin, DetailView):

    """ Show receipt data for ticket """

    template_name = 'ticket-receipt.html'
    pass


class TicketPayView(TicketReceiptView):

    """ Participant pay their ticket, or view a receipt. """

    template_name = 'ticket-pay.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):

        return super(TicketPayView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """populate data for the payment system."""
        ticket = self.object
        site = get_current_site(self.request)
        item_name = 'Metamorfozes 2014 ticket for %s' % ticket.get_full_name()
        paypal_dict = {
            'item_name': item_name,
            'amount': ticket.ticket_type.price,
            'item_description': item_name,
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'currency_code': ticket.ticket_type.currency,
            'lc': ticket.nationality,
            'country': ticket.nationality,
            'no_shipping': '1',  # Do not prompt for an address.
            'page_style': 'Metamorfozes_2014',
            'invoice': ticket.uuid,
            'notify_url': 'http://%s%s' % (site.domain, reverse('paypal-ipn')),
            'return_url': 'http://%s%s' % (site.domain, reverse('ticket-pay', kwargs={'uuid': ticket.uuid})),
            'cancel_return': 'http://%s%s' % (site.domain, reverse('ticket-pay', kwargs={'uuid': ticket.uuid})),
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict,)

        context = super(TicketPayView, self).get_context_data(**kwargs)
        context['debug'] = settings.DEBUG
        context['sold_out'] = Ticket.objects.sold_out()
        context['paypal_form'] = paypal_form
        return context


@csrf_exempt
def paypal_return(request):  # TODO fix uuid
    """
    Default return url from PayPal IPN.
    """
    # ticket = Ticket.objects.get(user=request.user)
    if request.GET.get('st') == u'Completed':
        messages.success(
            request,
            _(u'Your transaction has been completed, and a receipt for your purchase has been emailed to you.'))
    elif request.GET.get('st') == u'Pending':
        messages.success(
            request, _(
                u'Your transaction is pending, and a receipt for your purchase has been '
                u'emailed to you. Your account will be activated as soon as we have received '
                u'confirmation of your payment. If you have any questions, please contact us at '
                u'info@knutepunkt.org'))
    else:
        messages.error(request, _(u'The transaction was not completed.'))
    return render(request, 'signup_payment_success.html',)


@csrf_exempt
def paypal_cancel(request):
    """
    Return url from PayPal IPN when transaction is cancelled by user.
    """
    messages.error(request, _(u'The transaction was cancelled'))
    return HttpResponseRedirect(reverse('ticket-receipt'))


def calculate_data():
    """ Create a 2-dimensional list of participants, games and priorities to turn into a csv. """
    participants = Ticket.objects.filter(activated=True).order_by('last_name', 'first_name')
    games = Activity.objects.filter(published=True)
    priorities = ActivityPriority.objects.all()
    firstrow = [''] + [p.get_full_name() for p in participants]
    matrix = [firstrow]
    for g in games:
        row = [g.title]
        for p in participants:
            priority = priorities.filter(ticket=p, activity=g)
            if priority.count() == 1:
                number = str(priority[0].priority)
            else:
                number = ''
            row += [number]
        matrix += [row]
    return matrix

    from django.http import HttpResponse
    from django.template import loader, Context


def priorities_csv(request):
    """Create the HttpResponse object with the appropriate CSV header."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="metamorfozes.csv"'

    separator = ',' if 'comma' in request.GET else ';'
    quote = '"' if 'quote' in request.GET else ''

    csv_data = calculate_data()
    t = loader.get_template('csv-template.txt')
    c = Context({
        'data': csv_data,
        'separator': separator,
        'quote': quote,
    })
    response.write(t.render(c))
    return response
