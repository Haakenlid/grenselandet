from django.contrib import admin
from .models import Convention
from applications.tickets.admin import TicketPoolInline

# Register your models here.


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'location',
        'start_time',
        'end_time',
        'ticket_sales_opens',
        'ticket_sales_closes',
        'program_signup_opens',
        'program_signup_closes',
    ]
    # list_editable = [
    #     'ticket_sales_opens',
    #     'ticket_sales_closes',
    #     'program_signup_opens',
    #     'program_signup_closes',
    # ]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'mail_signature',
                'location',
                ('start_time', 'end_time'),
                ('ticket_sales_opens', 'ticket_sales_closes'),
                ('program_signup_opens', 'program_signup_closes'),
            ),
        }),
    )

    inlines = [
        TicketPoolInline,
    ]
