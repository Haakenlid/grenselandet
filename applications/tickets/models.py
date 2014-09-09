# -*- coding: utf-8 -*-
"""
Models and signals for the activity_priority app.
"""
import logging
from datetime import datetime
from hashids import Hashids
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.urlresolvers import reverse
from applications.conventions.models import Convention
from django_countries.fields import CountryField

from applications.mail.models import MailTrigger

class Person(models.Model):
    name = models.CharField(max_length=100)
# from annoying.functions import get_object_or_None
# import paypal.standard.ipn.signals as signals
# from paypal.standard.ipn.models import PayPalIPN
# from django.contrib.auth.models import User

# logger = logging.getLogger('metamorfozes')
BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
CURRENCY_CHOICES = (('EUR', '€'), ('NOK', 'NOK'), ('USD', 'US $'), ('LTL', 'LTL'),)


class Payment(models.Model):

    """ Transaction of payment for ticket. """

    ticket = models.ForeignKey('Ticket')
    # paypal_ipn = models.ForeignKey(PayPalIPN, null=True)
    sum_paid = models.IntegerField()
    paid_via = models.CharField(
        help_text=_('How was the payment made?'),
        max_length=50)
    payment_time = models.DateTimeField(
        auto_now=True,
        verbose_name='Time the ticket was paid.')

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __unicode__(self):
        """ unicode. """
        return u'%s, %s' % (self.ticket, self.sum_paid)


class TicketManager(models.Manager):

    hasher = Hashids(min_length=8, salt='aøsldkfjsdølkf')

    def get_by_hashid(self, hashid):
        return self.get(pk=self.dehash(hashid))

    def sold_out(self):
        """ Check if all tickets are sold out. """
        paying_participants = self.filter(activated=True).count()
        return paying_participants >= self.ticket_type.max

    def hash(self, value):
        return self.hasher.encrypt(value)

    def dehash(self, value):
        return self.hasher.decrypt(value)

    def delete_unpaid(self, min_age=24):
        from datetime import timedelta
        from django.utils import timezone
        expiration_date = timezone.now() - timedelta(hours=min_age)
        unpaid_tickets = self.filter(activated=False, order_time__lte=expiration_date)
        unpaid_tickets.update(status=Ticket.CANCELLED)


class Ticket(models.Model):

    """ Specific information about participants and their ticket. """

    ORDERED = 1
    PAID = 2
    CANCELLED = 0
    STATUS_CHOICES = (
        (ORDERED, _('ordered'),),
        (PAID, _('paid'),),
        (CANCELLED, _('cancelled'),),
    )

    objects = TicketManager()

    first_name = models.CharField(
        max_length=100,
        null=True,
    )
    last_name = models.CharField(
        max_length=100,
        null=True,
    )
    email = models.EmailField(
        null=True,
    )
    address = models.CharField(
        max_length=500,
        help_text=_('home address'),
    )
    country = CountryField()
    date_of_birth = models.DateField(
        null=True,
    )
    sum_paid = models.PositiveSmallIntegerField(
        default=0,
    )
    status = models.PositiveSmallIntegerField(
        default=CANCELLED,
        choices=STATUS_CHOICES,
        help_text=_('Status of payment.'),
    )
    order_time = models.DateTimeField(
        auto_now_add=True,
        help_text='Time the ticket was ordered',
    )
    ticket_type = models.ForeignKey(
        'TicketType',
        related_name='tickets',
    )
    comments = models.TextField(blank='True')

    def __unicode__(self):
        """unicode"""
        return u'%s %s, %s' % (self.first_name, self.last_name, self.ticket_type)

    def pay(self, *args, **kwargs):
        """ Make payment on ticket. """
        sum_paid = kwargs['sum_paid']
        currency = kwargs.pop('currency')
        if self.ticket_type.currency != currency is not None:
            raise ValueError(
                'Expected currency %s, received %s' % (
                    self.ticket_type.currency, currency))
        payment = Payment(ticket=self, *args, **kwargs)
        payment.save()
        self.sum_paid += sum_paid
        self.save()

    @property
    def age(self, at_date=None):
        """ Calculte age of participant """
        if not self.date_of_birth:
            return 0
        if at_date is None:
            at_date = datetime.now()
        return (
            at_date.year -
            self.date_of_birth.year -
            int(
                (at_date.month, at_date.day) <
                (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    @property
    def convention(self):
        return self.ticket_type.ticket_pool.convention

    @property
    def hashid(self):
        return self.objects.tickethash.encrypt(self.pk)

    def get_full_name(self):
        """Return full name of ticket holder."""
        return u'%s %s' % (self.first_name, self.last_name,)

    def get_absolute_url(self):
        """ Payment or receipt view. """
        hashid = self.objects.hash(self.pk)
        if self.activated:
            return reverse(viewname='ticket-receipt', kwargs={'hashid': hashid})
        else:
            return reverse(viewname='ticket-pay', kwargs={'hashid': hashid})

    def save(self, *args, **kwargs):
        """
        Selects ticket type based on ticket holder's nationality.
        And checks if ticket has been paid for.
        """
        if not self.ticket_type and self.nationality:
            self.ticket_type = (
                TicketType.objects.filter(nation_default__contains=self.nationality).first() or
                TicketType.objects.filter(nation_default__contains='*').first() or
                TicketType.objects.first() or
                None
            )
        if self.ticket_type and self.ticket_type.price <= self.sum_paid:
            self.status = self.PAID

        super(Ticket, self).save(*args, **kwargs)

class TicketPool(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    max_tickets = models.PositiveSmallIntegerField()
    convention = models.ForeignKey(Convention)
    class Meta:
        verbose_name = _('ticket pool')
        verbose_name_plural = _('ticket pools')

    def __unicode__(self):
        return self.name

    @property
    def sold_out(self):
        return self.max_tickets <= self.tickets_sold

    @property
    def tickets_sold(self):
        return self.ticket_types.tickets.exclude(status=Ticket.CANCELLED).count()


class TicketType(models.Model):

    """ Different ticket types for different participants. """
    name = models.CharField(max_length=20,)
    price = models.PositiveSmallIntegerField(default=0,)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3)
    ticket_pool = models.ForeignKey(TicketPool)
    max_tickets = models.PositiveSmallIntegerField(
        blank=True, null=True
        )

    description = models.CharField(
        help_text=_('Short description of the ticket type.'),
        max_length=200,
        blank=True,
    )
    @property
    def sold_out(self):
        if self.ticket_pool.sold_out:
            return True
        elif self.max_tickets:
            return self.max_tickets <= self.tickets_sold

    @property
    def tickets_sold(self):
        return self.tickets.exclude(status=Ticket.CANCELLED).count()

    def __unicode__(self):
        """ Return ticket name and price. """
        return '{con}:{tickettype} ({price} {currency})'.format(
            con=self.convention,
            tickettype=self.name,
            price=self.price,
            currency=self.currency,
        )




def payment_success(sender, **kwargs):
    """
    Trigger on signal from PayPal when payment is successful.
    """
    myTicket = Ticket.objects.get(uuid=sender.invoice)
    myTicket.pay(sum_paid=sender.mc_gross, currency=sender.mc_currency, paypal_ipn=sender, paid_via=u'paypal')
    MailTrigger.send_mail(recipient=self, trigger=MailTrigger.TICKET_PAID)


# signals.payment_was_successful.connect(payment_success)


def payment_fail(sender, **kwargs):
    """
    Trigger on signal from PayPal when payment is not successful.
    """
    myTicket = Ticket.objects.get(uuid=sender.invoice)
    logger.debug(u'payment was flagged\r %s\r%s' % (sender, myTicket, ))

# signals.payment_was_flagged.connect(payment_fail)

def send_ticket_email(ticket, template, subject):
    """ Send a payment receipt to the ticket buyer. """
    from django.template.loader import render_to_string
    from django.core.mail import send_mail

    context = {
        'ticket': ticket,
        'priorities': ticket.priorities.all().order_by('-priority'),
    }
    email_body = render_to_string(template, context)
    send_mail(
        subject=subject,
        message=email_body,
        from_email='',
        recipient_list=[ticket.email],
    )
