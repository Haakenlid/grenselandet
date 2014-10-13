from django.contrib.auth.models import User, Group
from django.db import models
from datetime import timedelta
from applications.conventions.models import Convention
from applications.tickets.models import Ticket

from django.utils.translation import ugettext_lazy as _


def next_convention():
    return Convention.objects.next().pk or None


def next_convention_start_time():
    convention = Convention.objects.next()
    if convention:
        return convention.start_time
    else:
        return None


class ItemType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(blank=True, max_length=1000)
    color = models.CharField(
        max_length=7, default="#FFF", help_text="html colour")
    ordering = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def css_class(self):
        return "program_" + self.name.lower().replace(" ", "")

    class Meta:
        ordering = ["ordering", "name", ]


class Participant(models.Model):
    user = models.ForeignKey(User)
    convention = models.ForeignKey(Convention)

    def __str__(self):
        return '{user}: {convention}'.format(
            user=self.user.get_full_name(),
            convention=self.convention.name,
        )

    def send_welcome_message(self, password=None):
        print('welcome, %s, %s' % (self, password))

    def make_organiser(self):
        organisers = Group.objects.get_or_create(
            name='{event} organisers'.format(
                event=self.convention.name)
        )
        self.user.is_staff = True
        self.user.save()
        organisers.user_set.add(self.user)

    @classmethod
    def create(cls, ticket):
        first_name = ticket.first_name.title()
        last_name = ticket.last_name.title()
        email = ticket.email.lower()
        convention = ticket.convention
        new_password = None

        user, is_new = User.objects.get_or_create(
            email=email,
        )

        if is_new:
            new_password = User.objects.make_random_password()
            user.first_name = first_name
            user.last_name = last_name
            user.username = user.email.split('@')[0]
            user.set_password(new_password)
            user.save()

        participant = cls.objects.create(
            user=user,
            convention=convention,
        )
        participant.send_welcome_message(new_password)
        return participant

    @classmethod
    def activate_all_tickets(cls):
        for ticket in Ticket.objects.all():
            cls.create(ticket)


class Location(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True, max_length=5000)
    max_capacity = models.IntegerField(
        blank=True, null=True,
    )
    ordering = models.IntegerField(default=0)
    convention = models.ForeignKey(
        Convention,
        related_name='event',
        default=next_convention,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["ordering", "name", ]


class ProgramItem(models.Model):
    DEFAULT_LENGTH = 60 * 4
    PROGRAM_TYPES = (
        ('Larp', 'Larp'),
        ('Freeform', 'Freeform game'),
        ('Workshop', 'Workshop'),
        ('Lecture', 'Lecture'),
        ('Social', 'Social event'),
        ('Other', 'Other'),
    )
    LANGUAGES = (
        ('EN', 'English'),
        ('NO', 'Scandinavian'),
    )
    convention = models.ForeignKey(
        Convention,
        default=next_convention,
    )
    name = models.CharField(
        max_length=100,
        help_text='The name of this programme item',
    )
    description = models.TextField(
        help_text='Description of the event',
    )
    item_type = models.ForeignKey(ItemType)

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES,
        default=LANGUAGES[0][0],
    )
    start_time = models.DateTimeField(
        default=next_convention_start_time
    )
    duration = models.PositiveSmallIntegerField(
        default=DEFAULT_LENGTH,
        help_text='Length in minutes',
    )
    location = models.ManyToManyField(
        Location,
        blank=True,
    )

    organisers = models.ManyToManyField(
        User,
        related_name='organised_by',
    )

    max_participants = models.IntegerField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def make_session(self):
        session = ProgramSession(
            programitem=self,
            location=self.location.first(),
            start_time=self.start_time,
        )
        session.save()

    def migrate_organisers(self):
        for o in self.organisers.all():
            u = o.user
            self.organizers.add(u)
            for s in self.programsession_set.all():
                signup, new = Signup.objects.get_or_create(
                    participant=u,
                    session=s,
                )
                signup.status = Signup.GAME_MASTER
                signup.save()


class ProgramSession(models.Model):
    programitem = models.ForeignKey(
        ProgramItem,
    )
    location = models.ForeignKey(
        Location,
    )
    start_time = models.DateTimeField(
        default=next_convention_start_time
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        through='Signup',
    )

    @property
    def max_participants(self):
        return self.programitem.max_participants

    @property
    def duration(self):
        return self.programitem.duration

    @property
    def end_time(self):
        return self.start_time + timedelta(
            minutes=self.programitem.duration,
        )

    def __str__(self):
        return '{item}: {time} {location}'.format(
            item=self.programitem,
            time=self.start_time,
            location=self.location,
        )

    def game_masters(self):
        return self.signup_set.filter(status=Signup.GAME_MASTER).count()

    def assigned_participants(self):
        return self.signup_set.exclude(status=Signup.NOT_ASSIGNED).order_by('-status', '-priority')

    def participants_signed_up(self):
        return self.signup_set.exclude(priority=0).count()

    def pixelheight(self):
        return int(self.duration / 2 - 1)


class Signup(models.Model):
    GAME_MASTER = 1
    PARTICIPANT = 2
    NOT_ASSIGNED = 0

    STATUS_CHOICES = (
        (GAME_MASTER, _('Game Master'),),
        (PARTICIPANT, _('Player'),),
        (NOT_ASSIGNED, _('Not assigned'),),
    )

    class Meta:
        unique_together = (
            ("session", "participant",),
        )
        ordering = [
            "-status",
            "-ordering",
            "-priority",
        ]

    session = models.ForeignKey(ProgramSession)
    participant = models.ForeignKey(User)
    updated = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(
        default=0,
        help_text="chosen by the user",
    )
    status = models.IntegerField(
        default=NOT_ASSIGNED,
        choices=STATUS_CHOICES,
    )
    ordering = models.IntegerField(
        default=0,
        help_text="Order on the list. To be calculated by an algorithm.",
    )

    def choice_number(self):
        return self.participant.signup_set.filter(priority__gt=self.priority).count() + 1

    def __str__(self):
        return '{item}: {status} {person} ({priority})'.format(
            item=self.session,
            status=self.get_status_display(),
            person=self.participant,
            priority=self.priority,
        )
