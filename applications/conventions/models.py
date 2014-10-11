from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import formats
from django.utils import timezone

# Create your models here.


class ConventionManager(models.Manager):

    def next(self):
        """ The upcoming event """
        next_convention = self.exclude(end_time__lt=timezone.now()).order_by('start_time').first()
        return next_convention


class Convention(models.Model):

    """ A con, festival or event """

    name = models.CharField(max_length=100)
    description = models.TextField()
    mail_signature = models.TextField()
    # logo
    # TODO: logo som sorl-greie
    location = models.CharField(max_length=500)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ticket_sales_opens = models.DateTimeField()
    ticket_sales_closes = models.DateTimeField()
    program_signup_opens = models.DateTimeField()
    program_signup_closes = models.DateTimeField()

    objects = ConventionManager()

    class Meta:
        verbose_name = _('Convention')
        verbose_name_plural = _('Conventions')

    def __str__(self):
        return self.name

    def ticket_sales_has_started(self):
        return timezone.now() > self.ticket_sales_opens

    def ticket_sales_has_ended(self):
        return timezone.now() > self.ticket_sales_closes

    def full_description(self):
        return '{name}\n{description}\n{start} to {end}'.format(
            name=self.name,
            description=self.description,
            start=formats.date_format(self.start_time, 'SHORT_DATE_FORMAT'),
            end=formats.date_format(self.end_time, 'SHORT_DATE_FORMAT'),
        )

