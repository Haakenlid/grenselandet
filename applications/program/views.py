# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import time
from django.core.urlresolvers import reverse
from django.db.models import Min
from django.shortcuts import get_object_or_404
# import random
from .models import *
from applications.conventions.models import Convention
from applications.tickets.models import Ticket
from .lottery import fordeling
# from django.contrib.auth.decorators import permission_required
# from django.contrib.auth.models import Group

from django.contrib.admin.views.decorators import staff_member_required

BLOCK_LENGTH = 30  # minutes
PIXELS_PER_BLOCK = 20


def pixelheight(duration):
    return int(duration / BLOCK_LENGTH * PIXELS_PER_BLOCK)


def hashid_schedule(request, hashid):
    ticket = get_object_or_404(Ticket, hashid=hashid)
    try:
        participant = Participant.objects.get(email=ticket.email)
    except (ObjectDoesNotExist,):
        participant = Participant.create(ticket)
    return schedule_for_user(request, participant)


def schedule(request):
    user = request.user
    if user.is_authenticated():
        participant = Participant.objects.get(pk=user.pk)
    else:
        participant = None
    return schedule_for_user(request, participant)


def schedule_for_user(request, participant):
    volunteer = False
    convention = Convention.objects.first()
    if timezone.now() > convention.program_signup_opens:
        registration_open = True
    else:
        registration_open = False
    if timezone.now() < convention.program_signup_closes:
        registration_closed = False
    else:
        registration_closed = True

    # sessions = ProgramSession.objects.exclude(programitem__itemtype__name="Work")
    sessions = ProgramSession.objects.all()
    if participant:
        # if participant.groups.filter(name__icontains="Volunteers"):
        #     sessions = ProgramSession.objects.all()
        #     volunteer = True
        updatelist = []
        for s in sessions.exclude(participants=participant):
            updatelist += [Signup(session=s, participant=participant)]

        if updatelist:
            Signup.objects.bulk_create(updatelist)

    dates = convention.dates()
    blocklength = timedelta(minutes=30)
    schedule = []

    for day in dates:

        timetable = []
        daystart = day.replace(hour=3)
        dayend = daystart + timezone.timedelta(hours=24)
        day_sessions = sessions.filter(
            start_time__gte=daystart,
            start_time__lt=dayend)
        if request.user.is_staff:
            locations = Location.objects.private()
        else:
            locations = Location.objects.public()

        day_rooms = locations.filter(
            programsession__start_time__gte=daystart,
            programsession__start_time__lt=dayend).distinct()
        blockstart = day_sessions.aggregate(Min('start_time'))["start_time__min"]
        last_hour = blockstart
        if not blockstart:
            continue

        while blockstart < dayend:  # all hours of the day
            blockend = blockstart + blocklength
            hour = [(blockstart, blockend,)]  # first cell in table
            timetable += [hour]
            events = sessions.select_related('location').filter(
                start_time__gte=blockstart,
                start_time__lt=blockend,
            )
            eventlocations = [e.location for e in events]

            for room in day_rooms:
                if room in eventlocations:
                    session = events.filter(location=room)[0]
                    if session.end_time > last_hour:
                        last_hour = session.end_time
                    if participant and registration_open:
                        s = Signup.objects.get(session=session, participant=participant)
                    else:
                        s = None

                    stars = session.programitem.item_type.stars

                    hour += [{
                        "session": session,
                        "stars": stars,
                        "signup": s,
                        "gamemasters": session.game_masters(),
                        "height": pixelheight(session.duration),
                    }]
                else:
                    hour += [None]  # empty cell
            blockstart = blockend  # next block

        while timetable[-1][0][1] > last_hour:
            timetable = timetable[:-1]  # cut off empty hours

        schedule += [{
            "rooms": day_rooms,
            "columns": len(day_rooms) + 1,
            "day": day,
            "daystart": daystart,
            "dayend": last_hour,
            "timetable": timetable,
        }]

    context = {
        "registration_open": registration_open,
        "registration_closed": registration_closed,
        "convention": convention,
        "volunteer": volunteer,
        "participant": participant,
        "GAME_MASTER": Signup.GAME_MASTER,
        "PIXELS_PER_BLOCK": PIXELS_PER_BLOCK,
        "blocklength": int(blocklength.total_seconds() / 60),
        "schedule": schedule,
    }

    return render(request, "schedule.html", context)


# @staff_member_required
def reshuffle(request):
    fordeling(Convention.objects.first())  # fordeler plasser
    return HttpResponseRedirect(reverse('program-schedule'))


@staff_member_required
def sessionlist(request):
    context = {
        "sessions": ProgramSession.objects.all()
    }

    return render(request, "sessionlist.html", context)


def public_list(request):
    context = {
        "sessions": ProgramSession.objects.exclude(
            programitem__name__icontains='vacant').exclude(
            programitem__itemtype__name__icontains='social')}

    return render(request, "open_list.html", context)


@staff_member_required
def participantlist(request):
    context = {
        "participants": list(
            Participant.objects.all().order_by(
                'first_name',
                'last_name').prefetch_related('signup_set'))}

    return render(request, "participantlist.html", context)


def blekke(request):
    programitems = Item.objects.exclude(itemtype='SOC').order_by('start_time')
    schedule = Item.objects.extra(select={'start_day': 'date(start_time)'},
                                  order_by=['start_day', 'location', 'start_time'])

    # schedule = Item.objects.all().order_by('start_time','location',)
    return render(request, "blekke.html",
                  {"programitems": programitems, 'schedule': schedule, },)


def program_oppslag(request):
    programitems = Item.objects.filter(max_participants__gte=1).order_by("start_time")
    for p in programitems:
        setattr(p, "list", p.attends_set.exclude(place_on_list=0).order_by('place_on_list'))

    return render(request, "oppslag.html", {"programitems": programitems})
