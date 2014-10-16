# coding=utf8

from applications.program.models import *
import random
from django.conf import settings


def fordeling():
    session_queryset = ProgramSession.objects.filter(programitem__max_participants__gt=0)
    reset_gamemasters()  # set priority to 0
    reset_assignments()  # unassign participants and extra signups.
    list_of_participants = initialise_participants(session_queryset)
    dict_of_sessions = initialise_sessions(session_queryset)
    assign_participants(list_of_participants, dict_of_sessions)
    update_sessions(dict_of_sessions)


def finn_ledig_plass(participant, dict_of_sessions):
    if len(participant['prioritised signups']) != 0:
        update_overlap = False
        my_signup = participant['prioritised signups'].pop(0)  # øverste spill på ønskelista
        session_dict = dict_of_sessions[my_signup.session.id]  # spillet
        if my_signup.status == Signup.GAME_MASTER:  # Spilleder
            participant['sessions that overlap'].update(
                session_dict['sessions that overlap'])
            finn_ledig_plass(participant, dict_of_sessions)  # ser om det er ledig på neste i bunken.
        else:
            if session_dict['program session'] in participant['sessions that overlap']:
                session_dict['assumed noshows'].append(my_signup)  # havner på ekstraliste
                finn_ledig_plass(participant, dict_of_sessions)  # ser om det er ledig på neste i bunken.
            else:
                if session_dict['full'] == False:  # ledig plass
                    participant['sessions that overlap']. update(
                        session_dict['sessions that overlap']. union(
                            session_dict['sibling sessions']))
                    session_dict['assigned signups'].append(my_signup)  # participanten fikk plass
                    my_signup.ordering = len(session_dict['assigned signups'])
                    if my_signup.status == Signup.NOT_ASSIGNED:
                        my_signup.status = Signup.PARTICIPANT
                    # my_signup.save()

                    if (len(session_dict['assigned signups']) >=
                            session_dict['max participants']):
                        session_dict['full'] = True  # da er spillet fullt
                else:  # ikke ledig plass
                    session_dict['assigned signups'].append(my_signup)  # havner på lista likevel
                    my_signup.ordering = len(session_dict['assigned signups'])
                    my_signup.status = 0
                    finn_ledig_plass(participant, dict_of_sessions)  # ser om det er ledig på neste

        if update_overlap:  # Refaktoriser til metode

            participant['sessions that overlap'].update(
                session_dict['sessions that overlap'])  # legger til i settet

        if(settings.DEBUG):
            print(
                session_dict['program session'].programitem,
                my_signup.participant.get_full_name(),
                my_signup.ordering,
                my_signup.get_status_display(),
            )

        my_signup.save()
        return True
    return False


def reset_gamemasters():
    gamemasters = Signup.objects.filter(
        status__in=[Signup.GAME_MASTER]
    )
    gamemasters.update(priority=0)


def initialise_participants(session_queryset):

    list_of_participants = []
    for participant in Participant.objects.all():
        participant_dict = {
            'participant': participant,
            'sessions that overlap': set(),
            'prioritised signups': list(
                participant.signup_set.filter(
                    session__in=session_queryset,
                ).order_by(
                    '-status',  # TODO: Er muligens ikke riktig.
                    '-priority',
                    '-session__programitem__max_participants',
                    '?',
                )
            ),
        }
        list_of_participants += [participant_dict]

    return list_of_participants


def initialise_sessions(session_queryset):
    dict_of_sessions = {}
    for my_session in session_queryset:
        starts_before_end = session_queryset.filter(
            start_time__lt=my_session.end_time
        )
        overlaps = set(
            [s for s in starts_before_end if s.end_time > my_session.start_time]
        )
        sibling_sessions = set(
            my_session.programitem.programsession_set.all()
        )

        session_dict = {
            'program session': my_session,
            'assigned signups': [],
            'assumed noshows': [],
            'estimated participant number': 0,
            'max participants': my_session.programitem.max_participants,
            'full': False,
            'sessions that overlap': overlaps,
            'sibling sessions': sibling_sessions,
        }

        dict_of_sessions[my_session.id] = session_dict

    for key, my_session in dict_of_sessions.items():
        for other_session in my_session['sessions that overlap']:
            dict_of_sessions[other_session.id]['sessions that overlap'].union(set(my_session))

    return dict_of_sessions


def assign_participants(list_of_participants, dict_of_sessions):
    not_finished = True
    random.shuffle(list_of_participants)  # TODO: Bedre rekkefølge.
    while not_finished:
        not_finished = False
        list_of_participants.reverse()
        for participant in list_of_participants:
            not_finished = not_finished or finn_ledig_plass(participant, dict_of_sessions)


def update_sessions(dict_of_sessions):
    for session_id in dict_of_sessions:
        my_session = dict_of_sessions[session_id]
        my_session['estimated participant number'] = len(
            my_session['assigned signups'])  # så mange som trolig dukker opp
        print(my_session['program session'], my_session['assigned signups'])
        my_session['assigned signups'] = my_session['assigned signups'] + \
            my_session['assumed noshows']  # legger ekstrafolk til i slutten


def reset_assignments():
    Signup.objects.filter(status=Signup.NOT_ASSIGNED, priority=0).delete()
    Signup.objects.all().update(ordering=0)
    Signup.objects.filter(status=Signup.PARTICIPANT).update(status=Signup.NOT_ASSIGNED)
    updatelist = []
    nothing = ProgramSession.objects.filter(programitem__item_type__name='NOTHING')
    for p in Participant.objects.all():
        for s in nothing.exclude(participants=p):
            updatelist += [
                Signup(session=s, participant=p)
            ]

    if updatelist:
        print('lager gatelangs', len(updatelist))
        Signup.objects.bulk_create(updatelist)


if __name__ == '__main__':
    import django
    django.setup()
    fordeling()
