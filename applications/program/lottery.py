# coding=utf8

from applications.program.models import ProgramSession, Participant, Signup
from applications.conventions.models import Convention
import random
from django.conf import settings
import logging
logger = logging.getLogger('debug')


def fordeling(convention):
    all_sessions = ProgramSession.objects.filter(programitem__convention=convention)
    # all_participants = Participant.objects.all()
    logger.info('resetting assignments')
    reset_assignments()  # unassign participants and extra signups.
    logger.info('initilising participants')
    list_of_participants = initialise_participants(all_sessions)
    logger.info('initilising sessions')
    session_dict = initialise_sessions(all_sessions)
    logger.info('assigning game masters')
    preassign_game_masters(list_of_participants, session_dict)
    logger.info('assigning players')
    assign_players(list_of_participants, session_dict)
    # logger.info('creating lists')
    # print_sessions(session_dict)


def print_sessions(session_dict):
    for session in session_dict.values():
        logger.info(session.programitem.name)
        for p in session.participant_list:
            logger.info(p)


def initialise_participants(session_queryset):
    list_of_participants = []
    for participant in Participant.objects.all():
        participant.check_missing_signup()
        participant.priority = 0
        participant.signups_remaining = participant.signup_set.filter(
            session__in=session_queryset,
        ).order_by(
            '-priority',
            'session__popularity',
            '?',
        )
        list_of_participants += [participant]
    return list_of_participants


def initialise_sessions(sessions):
    session_dict = {}
    for session in sessions:
        session.save()
        session.overlaps = session.same_time_sessions()
        session.sibling_sessions = ProgramSession.objects.filter(id=session.id)
        session.participant_list = []
        session_dict.update({session.id: session})
    return session_dict


def assign_players(list_of_participants, session_dict):
    random.shuffle(list_of_participants)
    list_of_participants.sort(key=lambda x: x.priority, reverse=True)
    # logger.info('participants: %d' % (len(list_of_participants)),)
    new_list = []

    for participant in list_of_participants:
        assigned = False

        while not assigned and participant.signups_remaining:
            top_choice = participant.signups_remaining.first()
            assigned = assign_to_session(top_choice, participant, session_dict)

        # logger.info('%s: %s'%(participant, participant.priority))
        if participant.signups_remaining:
            new_list.append(participant)

    if new_list:
        assign_players(new_list, session_dict)


def preassign_game_masters(list_of_participants, session_dict):
    for participant in list_of_participants:
        signups = participant.signups_remaining.exclude(status=Signup.NOT_ASSIGNED)
        for signup in signups:
            assign_to_session(signup, participant, session_dict)


def assign_to_session(signup, participant, session_dict):
    session = session_dict[signup.session.id]

    if signup.status != Signup.GAME_MASTER:
        signup.ordering = len(session.participant_list) + 1

    if signup.status == Signup.NOT_ASSIGNED:
        if len(session.participant_list) >= session.max_participants:
            signup.status = Signup.WAITING_LIST
        else:
            signup.status = Signup.PARTICIPANT

    signup.save()

    points = {
        Signup.GAME_MASTER: 3,
        Signup.PARTICIPANT: 0,
        Signup.PREASSIGNED: -2,
        Signup.VOLUNTEER: 2,
        Signup.WAITING_LIST: 2,
    }

    participant.priority += points[signup.status]

    if signup.status == Signup.WAITING_LIST:
        participant.signups_remaining = participant.signups_remaining.exclude(session=session)
        return False
    elif signup.status in [Signup.PARTICIPANT, Signup.PREASSIGNED]:
        session.participant_list.append(participant)
        participant.signups_remaining = participant.signups_remaining.exclude(session__in=session.sibling_sessions)
    participant.signups_remaining = participant.signups_remaining.exclude(session__in=session.overlaps)
    return True


def update_sessions(dict_of_sessions):
    for session_id in dict_of_sessions:
        my_session = dict_of_sessions[session_id]
        my_session['estimated participant number'] = len(
            my_session['assigned signups'])  # så mange som trolig dukker opp
        my_session['assigned signups'] = my_session['assigned signups'] + \
            my_session['waiting list']  # legger ekstrafolk til i slutten


def reset_assignments():
    Signup.objects.filter(status=Signup.NOT_ASSIGNED, priority=0).delete()
    Signup.objects.all().update(ordering=0)
    Signup.objects.filter(status__in=[Signup.PARTICIPANT, Signup.WAITING_LIST]).update(status=Signup.NOT_ASSIGNED)
    updatelist = []
    nothing = ProgramSession.objects.filter(programitem__item_type__name='NOTHING')
    for p in Participant.objects.all():
        for s in nothing.exclude(participants=p):
            updatelist += [
                Signup(session=s, participant=p)
            ]

    if updatelist:
        Signup.objects.bulk_create(updatelist)


if __name__ == '__main__':
    import django
    django.setup()
    fordeling(convention=Convention.objects.first())
