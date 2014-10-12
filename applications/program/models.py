from django.contrib.auth.models import User, Group
from django.db import models
from datetime import timedelta
from applications.conventions.models import Convention
from applications.tickets.models import Ticket


def next_convention():
    return Convention.objects.next().pk or None


def next_convention_start_time():
    convention = Convention.objects.next()
    if convention:
        return convention.start_time
    else:
        return None


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
    convention = models.ForeignKey(
        Convention,
        related_name='event',
        default=next_convention,
    )

    def __str__(self):
        return self.name

    # def save(self):
    #     if not self.convention:
    #         self.convention = Convention.objects.next()
    #     self.super().save()


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
    itemtype = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPES,
        default=PROGRAM_TYPES[0][0],
    )
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
    )
    location = models.ManyToManyField(
        Location,
        blank=True,
    )
    organisers = models.ManyToManyField(
        Participant,
        blank=True,
        related_name='organized_by',
    )
    participants = models.ManyToManyField(
        Participant,
        blank=True,
        through='Signup',
    )
    max_participants = models.IntegerField(
        blank=True, null=True,
    )

    @property
    def end_time(self):
        return self.start_time + timedelta(
            minutes=self.duration,
        )

    def __str__(self):
        return self.name

    # def save(self):
    #     if not self.convention:
    #         self.convention = Convention.objects.next()
    #     if not self.start_time:
    #         self.start_time = self.convention.start_time
    #     self.super().save()


class Signup(models.Model):
    programitem = models.ForeignKey(
        ProgramItem,
    )
    participant = models.ForeignKey(
        Participant,
    )
    signup_time = models.DateField(
        auto_now=True,
    )
    priority = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return '{item} -> {person} ({priority})'.format(
            item=self.programitem,
            person=self.participant,
            priority=self.priority,
        )
