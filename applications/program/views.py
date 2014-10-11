# -*- coding: utf-8 -*-
import random

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from applications.programme.models import Location, ProgramItem, Signup, Participant
from django.contrib.auth.models import User

from django.core.mail import send_mail
from random import choice
from django.http import HttpResponseRedirect


def spill_liste(request):
    programitems = ProgramItem.objects.all()
    return render_to_response(
        'signup/spill_liste.html',
        {'programitems': programitems,
         },
        context_instance=RequestContext(request),
    )


def deltager_liste(request, spill_id):
    programitems = ProgramItem.objects.all()
    myItem = programitems.get(id=spill_id)

    mySignups = myItem.signup_set.exclude(priority=0).order_by('priority')

    return render_to_response(
        'signup/deltager_liste.html',
        {'programitems': programitems,
         'myItem': myItem,
         'signups': mySignups},
        context_instance=RequestContext(request),
    )


def fordeling(request):

    p_list = []
    g_list = {}

    def finn_ledig_plass(person):
        if len(person['signups']) != 0:
            s = person['signups'].pop(0)  # øverste spill på ønskelista
            g = g_list[s.programitem.id]  # spillet
            if g['programitem'] not in person['games_that_overlap']:
                if g['full'] == False:
                    g['signups'].append(s)  # personen fikk plass
                    person['games_that_overlap'].update(g['games_that_overlap'])
                    if len(g['signups']) == g['programitem'].max_participants:
                        g['full'] = True  # da er spillet fullt
                else:
                    g['signups'].append(s)  # havner på lista likevel
                    finn_ledig_plass(person)  # ser om det er ledig på neste
            else:
                g['signups_overlap'].append(s)  # havner på ekstraliste
                finn_ledig_plass(person)  # ser om det er ledig på neste

    for p in Participant.objects.all():
        userObject = {'participant': p, 'signups': [], 'games_that_overlap': set(), }
        userObject['signups'] = list(p.signup_set.exclude(priority=0).order_by('priority'))
        p_list += [userObject]

    p_items = ProgramItem.objects.all()
    for g in p_items:
        gameObject = {
            'programitem': g,
            'signups': [],
            'signups_overlap': [],
            'will_show': 10,
            'games_that_overlap': [],
            'full': False}
        gameObject['games_that_overlap'] = set(p_items.filter(end_time__range=(g.start_time, g.end_time)))
        g_list[g.id] = gameObject

    for n in range(100):
        random.shuffle(p_list)  # det skal være lotteri så rekkefølgen blir tilfeldig for hver runde
        for person in p_list:
            finn_ledig_plass(person)

    for g_id in g_list:
        g = g_list[g_id]
        g['will_show'] = len(g['signups'])  # så mange som trolig dukker opp
        g['signups'] = g['signups'] + g['signups_overlap']  # legger ekstrafolk til i slutten

    return render_to_response('signup/fordeling.html', {'g_list': g_list, }, RequestContext(request),)


def sendmassemail(request):
    report = ''
    chars = 'abcdefghijklmnopqrstuvw1234567890'

    meldingstekst = """Dear %s
    http://program.grenselandet.net
    username: %s, password: %s"""

    for myUser in User.objects.all()[30:]:
        if not myUser.is_active:
            myUser.is_active = True
            myParticipant = Participant.objects.get_or_create(user=myUser)[0]
            for myGame in ProgramItem.objects.all():
                mySignup = Signup.objects.get_or_create(participant=myParticipant, programitem=myGame)[0]

            password = ''.join([choice(chars) for i in xrange(4)])
            myUser.set_password(password)
            myUser.save()
            report += '<p>%s:%s</p>' % (myUser.username, password)

            parsed_message = meldingstekst % (myParticipant, myUser.username, password)

            # send_mail('Subject here', parsed_message, 'haakenlid@grenselandet.com',
            # [myUser.email], fail_silently=False)

    return HttpResponse(report)


def signup_closed(request):
    myUser = request.user
    aktive = 0
    myGames = []
    optionlist = ['&nbsp;&nbsp;&nbsp;']
    myString = u''
    if not myUser.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=/')

    else:
        message = 'Welcome to Grenselandet'

    # har brukeren en participant?
    myParticipant = Participant.objects.get_or_create(user=myUser)[0]

    # gaa gjennom hvert spill

    mySignups = myParticipant.signup_set.exclude(priority=0).order_by('priority')

    # finne navn, beskrivelse, tid, id, spraak og paameldingsstatus
    # hvis det ikke finnes noen relasjon - opprett det

    return render_to_response(
        'signup/signup_closed.html',
        {
            'participant': myParticipant,
            'message': message,
            'mySignups': mySignups,
        },
        context_instance=RequestContext(request),
    )


def gamelist(request):
    myUser = request.user
    aktive = 0
    myGames = []
    optionlist = ['&nbsp;&nbsp;&nbsp', ]
    if not myUser.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=/')

    if request.method == 'POST':
        message = 'Thanks for registering your choices!'
        for myItem in request.POST.items():
            if myItem[0].isdigit():
                if not myItem[1].isdigit():
                    myItem = (myItem[0], 0)
                mySignup = Signup.objects.get(id=myItem[0])
                mySignup.priority = myItem[1]
                mySignup.save()
    else:
        message = 'Welcome to Grenselandet'

    # har brukeren en participant?
    myParticipant = Participant.objects.get_or_create(user=myUser)[0]

    # gaa gjennom hvert spill

    for myGame in ProgramItem.objects.all():
        mySignup = Signup.objects.get_or_create(participant=myParticipant, programitem=myGame)[0]
        myGames += [(myGame, mySignup)]
        if mySignup.priority != 0:
            aktive += 1
            optionlist += [str(aktive)]

    # finne navn, beskrivelse, tid, id, spraak og paameldingsstatus
    # hvis det ikke finnes noen relasjon - opprett det

    return render_to_response(
        'signup/gamelist.html',
        {
            'participant': myParticipant,
            'message': message,
            'myGames': myGames,
            'aktive': aktive,
            'optionlist': optionlist
        },
        context_instance=RequestContext(request),
    )
