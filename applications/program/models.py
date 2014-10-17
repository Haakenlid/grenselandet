import statistics
from django.contrib.auth.models import User, Group
from django.db import models
from datetime import timedelta
from applications.conventions.models import Convention
from applications.tickets.models import Ticket

from django.utils.translation import ugettext_lazy as _
from django.utils import formats


def next_convention():
    convention = Convention.objects.next()
    if convention:
        return convention.pk
    else:
        return None


def next_convention_start_time():
    convention = Convention.objects.next()
    if convention:
        return convention.start_time
    else:
        return None


class Participant(User):

    class Meta:
        proxy = True

    def __str__(self):
        return self.get_full_name()

#     def make_organiser(self):
#         organisers = Group.objects.get_or_create(
#             name='{event} organisers'.format(
#                 event=self.convention.name)
#         )
#         self.user.is_staff = True
#         self.user.save()
#         organisers.user_set.add(self.user)

    @classmethod
    def create(cls, ticket):
        first_name = ticket.first_name.title()
        last_name = ticket.last_name.title()
        email = ticket.email.lower()
        new_password = None

        participant, is_new = cls.objects.get_or_create(
            email=email,
        )

        if is_new:
            username = participant.email.split('@')[0]
            while Participant.objects.filter(username=username):
                username = username + "2"
            new_password = User.objects.make_random_password()
            participant.first_name = first_name
            participant.last_name = last_name
            participant.username = username
            participant.set_password(new_password)
            participant.save()

        return participant

    @classmethod
    def activate_all_tickets(cls):
        for ticket in Ticket.objects.all():
            cls.create(ticket)

    def recreate_signups(self):
        if not self.signup_set.count() >= 2:
            print(self, 'ingen')
            return
        for session in ProgramSession.objects.all():
            signup, new = Signup.objects.get_or_create(session=session, participant=self)
            if new and session.programitem.item_type.stars == 4:
                signup.priority = 4
                signup.save()
                print(signup)

    def assigned_games(self):
        return self.signup_set.exclude(status=Signup.NOT_ASSIGNED)

    def not_signed_up(self):
        """ Mark participant as not signed up """
        no_signups = ProgramSession.objects.filter(programitem__item_type__name__icontains='no signup')
        for session in no_signups:
            signups = Signup.objects.filter(
                participant=self, session=session.same_time_sessions(),
            ).exclude(
                status=Signup.NOT_ASSIGNED, priority=0,
            ).count()
            if signups == 0:
                signup, new = Signup.objects.get_or_create(participant=self, session=session)
                signup.priority = 1
                signup.status = Signup.PREASSIGNED
                signup.save()
            else:
                Signup.objects.filter(participant=self, session=session).delete()


class ItemType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(blank=True, max_length=1000)
    stars = models.PositiveSmallIntegerField(
        help_text=_('Max stars that participants can give during signup.'),
        default=4,
    )
    color = models.CharField(
        max_length=7, default="#FFF", help_text="html colour")
    ordering = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def css_class(self):
        return "program_" + self.name.lower().replace(" ", "")

    class Meta:
        ordering = ["ordering", "name", ]


class LocationManager(models.Manager):

    def public(self):
        return super().exclude(staff_only=True)

    def private(self):
        return super().all()


class Location(models.Model):
    objects = LocationManager()
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True, max_length=5000)
    max_capacity = models.IntegerField(
        blank=True, null=True,
    )
    staff_only = models.BooleanField(default=False)
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
        Participant,
        related_name='organised_by',
        blank=True,
    )

    max_participants = models.IntegerField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def assign_organisers_as_game_masters(self):
        for o in self.organisers.all():
            for s in self.programsession_set.all():
                signup, new = Signup.objects.get_or_create(
                    participant=o,
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
    end_time = models.DateTimeField(
        blank=True,
        null=True,
    )
    participants = models.ManyToManyField(
        Participant,
        blank=True,
        through='Signup',
    )
    popularity = models.FloatField(
        default=0.0,
    )

    def calculate_popularity(self):
        # signups = self.signup_set.order_by('-priority')[0:self.max_participants]
        # if signups:
        #     return statistics.mean(signups.values_list('priority', flat=True))
        signups = self.signup_set.filter(priority__gt=self.programitem.item_type.stars/2).count()
        if self.max_participants:
            return signups/self.max_participants
        elif self.signup_set.count():
            return signups/self.signup_set.count()
        else:
            return 0

    def same_time_sessions(self):
        sessions = ProgramSession.objects.exclude(
            start_time__gte=self.end_time).exclude(
            end_time__lte=self.start_time)
        return sessions

    def players(self):
        players = self.signup_set.exclude(status__in=(
            Signup.NOT_ASSIGNED, Signup.WAITING_LIST)
        ).order_by(
            'ordering').prefetch_related('participant')
        return players

    @property
    def max_participants(self):
        return self.programitem.max_participants

    @property
    def duration(self):
        return self.programitem.duration

    def save(self):
        self.end_time = self.start_time + timedelta(
            minutes=self.programitem.duration,
        )
        self.popularity = self.calculate_popularity()
        return super().save()

    def __str__(self):
        return '{item}: {time} {location}'.format(
            item=self.programitem,
            time=formats.date_format(self.start_time, 'SHORT_DATETIME_FORMAT'),
            location=self.location,
        )

    def game_masters(self):
        gamemasters = self.signup_set.filter(status=Signup.GAME_MASTER)
        return gamemasters
        # return [gm.participant.get_full_name() for gm in gamemasters]

    def game_masters_count(self):
        return self.game_masters().count()

    def assigned_participants(self):
        return self.signup_set.exclude(status=Signup.NOT_ASSIGNED).order_by('-status', '-priority')

    def participants_signed_up(self):
        return self.signup_set.exclude(priority=0).count()


class Signup(models.Model):
    GAME_MASTER = 1
    PARTICIPANT = 2
    PREASSIGNED = 3
    VOLUNTEER = 4
    WAITING_LIST = 5
    NOT_ASSIGNED = 0

    STATUS_CHOICES = (
        (GAME_MASTER, _('Game Master'),),
        (PREASSIGNED, _('Preassigned'),),
        (VOLUNTEER, _('Volunteer'),),
        (PARTICIPANT, _('Participant'),),
        (NOT_ASSIGNED, _('Not assigned'),),
        (WAITING_LIST, _('Waiting list'),),
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

    def validate_unique(self, *args, **kwargs):
        old = Signup.objects.filter(session=self.session, participant=self.participant)
        if old.count() == 1:
            old_signup = old[0]
            if old_signup.pk != self.pk:
                self.pk = old_signup.pk
                old_signup.delete()

        super().validate_unique(*args, **kwargs)

    session = models.ForeignKey(ProgramSession)
    participant = models.ForeignKey(Participant)
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
