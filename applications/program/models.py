from django.contrib.auth.models import User, Group
from django.db import models
from datetime import timedelta
from applications.conventions.models import Convention

NEXT_CONVENTION = Convention.objects.next()


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

    @staticmethod
    def create(cls, first_name, last_name, email, convention,):
        first_name = first_name.capitalise()
        last_name = last_name.capitalise()
        email = email.lowercase()
        new_password = None

        is_new, user = User.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        if is_new:
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()

        participant = cls.objects.create(
            user=user,
            convention=convention,
        )
        participant.send_welcome_message(new_password)
        return participant


class Location(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True, max_length=5000)
    max_capacity = models.IntegerField(blank=True)
    convention = models.ForeignKey(
        Convention,
        default=NEXT_CONVENTION,
    )

    def __str__(self):
        return self.name


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
        default=NEXT_CONVENTION,
    )
    name = models.CharField(
        max_length=100,
        help_text='The name of this programme item',
    )
    description = models.CharField(
        null=True,
        max_length=5000,
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
        default=NEXT_CONVENTION.start_time,
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
        blank=True,
    )

    @property
    def end_time(self):
        return self.start_time + timedelta(
            minutes=self.DEFAULT_LENGTH,
        )

    def __str__(self):
        return self.name


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
