from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail

from applications.conventions.models import Convention


class MailTemplate(models.Model):

    subject = models.TextField()
    body_text = models.TextField()
    # body_html = models.TextField()
    convention = models.ManyToManyField(
        Convention,
        through='MailTrigger',
        related_name='mail_to_participants',
    )

    class Meta:
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')

    def __unicode__(self):
        return self.subject

    # def get_absolute_url(self):
    #     return ('')

    def send_mail(self, recipient, convention):

        context = {
            'recipient': recipient,
            'convention': convention,
        }
        email_body = render_to_string(self.template, context)
        send_mail(
            subject=self.subject,
            message=email_body,
            from_email='',
            recipient_list=[recipient.email],
        )


class MailTrigger(models.Model):

    TICKET_ORDERED = 1
    TICKET_PAID = 2
    TICKET_CANCELLED = 3
    SIGNUP_OPEN = 4
    SIGNUP_CLOSED = 5
    PROGRAMME_ASSIGNED = 6

    TRIGGER_CHOICES = (
        (TICKET_ORDERED, _('ticket ordered'),),
        (TICKET_PAID, _('ticket paid'),),
        (TICKET_CANCELLED, _('ticket cancelled'),),
        (SIGNUP_OPEN, _('signup open'),),
        (SIGNUP_CLOSED, _('signup closed'),),
        (PROGRAMME_ASSIGNED, _('programme assigned'),),
    )

    convention = models.ForeignKey(
        Convention,
        related_name='mailtriggers',
    )
    template = models.ForeignKey(
        MailTemplate,
        related_name='mailtriggers',
    )
    trigger = models.PositiveSmallIntegerField(
        choices=TRIGGER_CHOICES,
    )

    class Meta:
        unique_together = ('convention', 'template', 'trigger')

    @classmethod
    def send_mail(cls, recipient, trigger):
        convention = recipient.convention
        try:
            trigger = cls.objects.get(trigger=trigger, convention=convention)
        except ObjectDoesNotExist:
            raise NotImplementedError('no such mail template')
        trigger.template.send_mail(recipient, convention)
