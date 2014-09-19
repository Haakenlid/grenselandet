# -*- coding: utf-8 -*-
"""
Models and signals for the activity_priority app.
"""
from datetime import datetime
from hashids import Hashids
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse
from applications.conventions.models import Convention
from django_countries.fields import CountryField
from applications.mail.models import MailTrigger


class Person(models.Model):
    name = models.CharField(max_length=100)
# from annoying.functions import get_object_or_None
# from django.contrib.auth.models import User

import logging
logger = logging.getLogger('debug')
BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
CURRENCY_CHOICES = (('EUR', '€'), ('NOK', 'NOK'), ('USD', 'US $'), ('LTL', 'LTL'),)


class Payment(models.Model):

    """ Transaction of payment for ticket. """

    ticket = models.ForeignKey('Ticket')
    sum_paid = models.IntegerField()
    currency = models.CharField(
        max_length=3
    )
    transaction_id = models.CharField(
        help_text=_('payment provider transaction id'),
        max_length=50,
        editable=False,
        null=True,
    )
    paid_via = models.CharField(
        max_length=50,
        help_text=_('How was the payment made?'),
    )
    payment_time = models.DateTimeField(
        auto_now=True,
        help_text=_('Time the ticket was paid.'),
    )

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        """ unicode. """
        return '{ticket}, {sum}'.format(
            ticket=self.ticket,
            sum=self.sum_paid,
        )


class TicketManager(models.Manager):

    def unpaid(self):
        return self.filter(status=Ticket.ORDERED)

    def sold_out(self):
        """ Check if all tickets are sold out. """
        paying_participants = self.filter(activated=True).count()
        return paying_participants >= self.ticket_type.max

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

    hasher = Hashids(min_length=8, salt='salte bjørner')

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
    city = models.CharField(
        max_length=500,
    )
    postal_code = models.CharField(
        max_length=500,
    )
    address = models.CharField(
        max_length=500,
    )
    country = CountryField()
    date_of_birth = models.DateField(
        null=True,
    )
    sum_paid = models.PositiveSmallIntegerField(
        default=0,
    )
    status = models.PositiveSmallIntegerField(
        default=ORDERED,
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
    hashid = models.CharField(
        max_length=100,
        db_index=True,
    )
    comments = models.TextField(blank='True')

    def __str__(self):
        return '{name}: {ticket_type}'.format(
            name=self.get_full_name(),
            ticket_type=self.ticket_type,
        )

    def pay(self, **kwargs):
        """ Make payment on ticket. """

        sum_paid = kwargs.pop('sum_paid', self.ticket_type.price)
        currency = kwargs.pop('currency', self.ticket_type.currency)

        if self.ticket_type.currency != currency is not None:
            raise ValueError(
                'Expected currency {}, received {}'.format(
                    self.ticket_type.currency,
                    currency,
                ))

        kwargs.update(
            ticket=self,
            sum_paid=sum_paid,
            currency=currency,
        )
        payment = Payment(**kwargs)
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

    def get_full_name(self):
        """Return full name of ticket holder."""
        return u'%s %s' % (self.first_name, self.last_name,)

    def get_address_display(self):
        """Return full name of ticket holder."""
        res = '{address}, {postal_code} {city}, {country}'.format(
            address=self.address,
            postal_code=self.postal_code,
            city=self.city,
            country=self.country.name,
        )
        return res

    def get_absolute_url(self):
        """ Payment or receipt view. """
        kwargs = {'hashid': self.hashid, }
        if self.status == self.ORDERED:
            return reverse(viewname='ticket-payment', kwargs=kwargs,)
        elif self.status == self.PAID:
            return reverse(viewname='ticket-receipt', kwargs=kwargs,)
        else:
            # Cancelled?
            return ''

    def save(self, *args, **kwargs):
        """
        Selects ticket type based on ticket holder's nationality.
        And checks if ticket has been paid for.
        """
        if self.status == self.ORDERED and self.ticket_type.price <= self.sum_paid:
            self.status = self.PAID
            MailTrigger.objects.send_mail(recipient=self, trigger=MailTrigger.TICKET_PAID)
        if self.status == self.PAID and self.ticket_type.price > self.sum_paid:
            self.status = self.ORDERED

        super().save(*args, **kwargs)

        if not self.hashid:
            self.ticket_type.check_availability()
            # import ipdb; ipdb.set_trace()
            self.hashid = self.hasher.encrypt(self.pk)
            super().save(*args, **kwargs)
            MailTrigger.objects.send_mail(recipient=self, trigger=MailTrigger.TICKET_ORDERED)


class TicketPool(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    max_tickets = models.PositiveSmallIntegerField()
    convention = models.ForeignKey(Convention)

    class Meta:
        verbose_name = _('ticket pool')
        verbose_name_plural = _('ticket pools')

    def __str__(self):
        return self.name

    def sold_out(self):
        return self.max_tickets <= self.tickets_sold

    @property
    def tickets_sold(self):
        return sum(
            tt.tickets.exclude(status=Ticket.CANCELLED).count()
            for tt in self.ticket_types.all()
        )


class TicketType(models.Model):

    """ Different ticket types for different participants. """

    COMING_SOON = 0
    FOR_SALE = 1
    SOLD_OUT = 2
    SECRET = 3
    STATUS_CHOICES = (
        (COMING_SOON, _('coming soon')),
        (FOR_SALE, _('for sale')),
        (SOLD_OUT, _('sold out')),
        (SECRET, _('secret')),
    )

    name = models.CharField(max_length=20,)
    price = models.PositiveSmallIntegerField(default=0,)
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3)
    ticket_pool = models.ForeignKey(
        TicketPool,
        related_name='ticket_types')
    max_tickets = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text=_('only needed if the quota on this ticket type is smaller than the assigned ticket pool.'),
    )
    slug = models.SlugField(
        editable=False,
        db_index=True,
    )

    description = models.CharField(
        help_text=_('Short description of the ticket type.'),
        max_length=200,
        blank=True,
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=SECRET,
    )

    def get_price_display(self):
        return '{price} {currency}'.format(price=self.price, currency=self.get_currency_display())

    def max(self):
        return self.max_tickets or self.ticket_pool.max_tickets

    def check_availability(self):
        if self.status == self.FOR_SALE and self.sold_out():
            self.status = self.SOLD_OUT
            self.save()
        return self.status

    def sold_out(self):
        if self.max() <= self.tickets_sold:
            return True
        if self.ticket_pool.sold_out():
            return True
        return False

    @property
    def tickets_sold(self):
        return self.tickets.exclude(status=Ticket.CANCELLED).count()

    def __str__(self):
        """ Return ticket name and price. """
        return '{tickettype} {con} ({price} {currency})'.format(
            con=self.ticket_pool.convention,
            tickettype=self.name,
            price=self.price,
            currency=self.currency,
        )

    def get_absolute_url(self):
        return reverse(
            viewname='ticket-booking',
            kwargs={'ticket_type_slug': self.slug},
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(r'{ticket_type}-{con}'.format(
            con=self.ticket_pool.convention.name,
            ticket_type=self.name,
        ))[:50]
        super().save(*args, **kwargs)
