from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import MailTemplate, MailTrigger
# from applications.tickets.admin import TicketPoolInline

# Register your models here.


class MailTriggerInline(admin.TabularInline):
    model = MailTrigger
    extra = 0



def test_mail_trigger(modeladmin, request, queryset):
    recipient = request.user
    for trigger in queryset:
        trigger.send_mail(recipient)

test_mail_trigger.short_description = _('send this mail to yourself.')


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'trigger',
        'subject',
        'body_text',
    ]
    list_editable = [
        'subject',
        'body_text',
    ]

    inlines = [
        MailTriggerInline,
    ]

    actions = [
        test_mail_trigger,
    ]


@admin.register(MailTrigger)
class MailTriggerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'convention',
        'template',
        'trigger',
    ]
    actions = [
        test_mail_trigger,
    ]
