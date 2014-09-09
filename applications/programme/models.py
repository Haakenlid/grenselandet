from django.db import models
from django.utils.translation import ugettext_lazy as _

PRIORITY_CHOICES = (
    1, _('not really'),
    2, _('why not?'),
    3, _('yes'),
    4, _('oh yeah!'),
    )

class Activity(models.Model):

    """
    Represents an activity at the festival that you can sign up for.
    """

    title = models.CharField(unique=True, max_length=100,)
    creators = models.CharField(blank=True, null=True, max_length=500,)
    description = models.TextField(blank=True, max_length=1000,)
    published = models.BooleanField(
        help_text=_('Is the activity published yet?'),
        default=False,)
    ordering = models.SmallIntegerField(
        help_text=_('Order to display this item in list.'),
        default=100)
    activity_priorities = models.ManyToManyField(
        'Ticket',
        help_text=_('Who has signed up for the activity.'),
        through='ActivityPriority',
        related_name='activities',
    )
    max_participants = models.SmallIntegerField(
        blank=True, null=True,
        help_text=_('Maximum number of participants at this activity.'),
    )

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ('ordering', '-published', 'pk',)

    def __unicode__(self):
        """unicode"""
        return u'%s – by %s' % (self.title, self.creators)

    def signedup(self):
        participants = self.priorities.filter(ticket__activated=True)
        result = []
        for stars in range(MAX_STARS, 0, -1):
            group = participants.filter(priority=stars)
            names = [p.ticket for p in group]
            result.append(names)
        return result

class ActivityPriority(models.Model):
    """
    Relationship Ticket <-> Activity.
    Describing how highly prioritised each game is.
    """

    ticket = models.ForeignKey('Ticket', related_name='priorities')
    activity = models.ForeignKey('Activity', related_name='priorities')
    # priority = models.PositiveSmallIntegerField(default=1)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=1)

    class Meta:
        verbose_name = _('activity priority')
        verbose_name_plural = _('activity priorities')
        ordering = ('activity',)

    def __unicode__(self):
        """ Returns 'Name - Game (number)' """
        return u'%s %s %d' % (self.ticket, self.activity, self.priority)

    def priority_stars(self):
        return '★' * self.priority