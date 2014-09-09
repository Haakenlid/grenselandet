from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Convention(models.Model):
    """ A con, festival or event """

    name = models.CharField(max_length=100)
    description = models.TextField()
    # logo
    # TODO: logo som sorl-greie
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ticket_sales_opens = models.DateTimeField()
    ticket_sales_closes = models.DateTimeField()
    program_signup_opens = models.DateTimeField()
    program_signup_closes = models.DateTimeField()

    class Meta:
        verbose_name = _('Convention')
        verbose_name_plural = _('Conventions')

    def __str__(self):
        return self.name

