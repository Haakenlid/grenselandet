"""
Admin for signups.
"""
from django.contrib import admin
from .models import *
from datetime import datetime
# from django.contrib.contenttypes import generic

CUTOFF_DATE = datetime(year=1986, month=10, day=25)  # Age cutoff TODO: don't hardcode this.


class Youth_filter(admin.SimpleListFilter):

    """ Filter on participants age. """

    title = ('Age')
    parameter_name = 'age'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('0-26', ('26 years or younger')),
            ('26+', ('27 years or older')),
        )

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '0-26':
            return queryset.filter(
                date_of_birth__gte=CUTOFF_DATE).order_by('-date_of_birth')
        if self.value() == '26+':
            return queryset.exclude(
                date_of_birth__gte=CUTOFF_DATE).order_by('-date_of_birth')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    """ Backend settings for Tickets. """

    list_display = (
        'first_name',
        'last_name',
        'ticket_type',
        'age',
        'order_time',
        'status',
        # 'nationality',
        'email',
        'sum_paid',
        'comments',
    )
    list_editable = (
        'status',
        'ticket_type',
        )
    search_fields = (
        # 'nationality',
        'first_name',
        'last_name',
    )
    list_filter = (
        Youth_filter,
        # 'nationality',
        )


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):

    """Backend settings for Ticket types."""

    list_display = (
        'id',
        'name',
        'price',
        'currency',
        # 'nation_default',
        'description',
    )

    list_editable = (
        'name',
        'price',
        'currency',
        # 'nation_default',
        'description',
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticket',
        'sum_paid',
        'payment_time',
        'paid_via',
        )
