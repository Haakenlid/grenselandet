from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.template import Template, Context

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

    def __str__(self):
        return self.subject

    # def get_absolute_url(self):
    #     return ('')
    def trigger(self):
        # TODO: sort by convention happening soon?
        return self.mailtriggers.first()

    def send_mail(self, recipient, convention=None):
        if not convention:
            convention = self.trigger().convention

        context = Context({
            'recipient': recipient,
            'convention': convention,
        })
        subject_template = Template(self.subject)
        body_template = Template(
            '{body}\n-- \n{signature}'.format(
                body=self.body_text,
                signature=convention.mail_signature,)
        )
        email_subject = subject_template.render(context)
        email_body = body_template.render(context)
        send_mail(
            subject=email_subject,
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
        unique_together = ('convention', 'trigger')

    def __str__(self):
        return '{con}: {trigger}'.format(con=self.convention, trigger=self.get_trigger_display())

    def send_mail(self, recipient):
        convention = self.convention
        self.template.send_mail(recipient, convention)

    # @classmethod
    # def send_mail(cls, recipient, trigger):
    #     convention = recipient.convention
    #     try:
    #         trigger = cls.objects.get(trigger=trigger, convention=convention)
    #     except ObjectDoesNotExist:
    #         raise NotImplementedError('no such mail template')
    #     trigger.template.send_mail(recipient, convention)
