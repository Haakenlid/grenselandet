# -*- coding: utf-8 -*-

from django.shortcuts import render
# from django.http import Http404, HttpResponseRedirect, HttpResponse
# from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import time
from django.db.models import Min
# import random
from .models import *
from applications.conventions.models import Convention
# from program.signupdistribution import fordeling
# from django.contrib.auth.decorators import permission_required
# from django.contrib.auth.models import Group

from django.contrib.admin.views.decorators import staff_member_required


def schedule(request):
    registration_open = True
    volunteer = False
    convention = Convention.objects.first()
    if timezone.now() > convention.program_signup_opens:
        # registration_open = False
        pass

    # sessions = ProgramSession.objects.exclude(programitem__itemtype__name="Work")
    sessions = ProgramSession.objects.all()
    u = request.user
    if u.is_authenticated():
        # if u.groups.filter(name__icontains="Volunteers"):
        #     sessions = ProgramSession.objects.all()
        #     volunteer = True
        updatelist = []
        for s in sessions.exclude(participants=u):
            updatelist += [Signup(session=s, participant=u)]

        if updatelist:
            Signup.objects.bulk_create(updatelist)

    dates = convention.dates()
    blocklength = timedelta(minutes=60)
    schedule = []

    for day in dates:

        timetable = []
        daystart = day.replace(hour=3)
        dayend = daystart + timezone.timedelta(hours=24)
        day_sessions = sessions.filter(
            start_time__gte=daystart,
            start_time__lt=dayend)
        day_rooms = Location.objects.filter(
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
                    newitem = events.filter(location=room)[0]
                    if newitem.end_time > last_hour:
                        last_hour = newitem.end_time
                    if u.is_authenticated() and registration_open:
                        s = Signup.objects.get(session=newitem, participant=u)
                    else:
                        s = None

                    hour += [{
                        "session": newitem,
                        "signup": s,
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
        "volunteer": volunteer,
        "GAME_MASTER": Signup.GAME_MASTER,
        "blocklength": int(blocklength.total_seconds() / 60),
        "schedule": schedule,
    }

    return render(request, "schedule.html", context)


@staff_member_required
def reshuffle(request):
    fordeling()  # fordeler plasser
    return render(request, "reshuffle.html",)


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
        "users": list(User.objects.all().order_by('first_name', 'last_name'))
    }

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
