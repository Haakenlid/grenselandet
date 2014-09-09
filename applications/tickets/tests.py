"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import datetime
from .models import *
from .forms import *
from .views import *


class BuyTicketTest(TestCase):

    """ Buys a ticket in the system. """

    def bookTicket():
        """ Books one ticket """
        myTicket = Ticket(
            first_name=u'Håken',
            last_name=u'Lid',
            nationality=u'NO',
            date_of_birth=datetime.date(1980, 0o1, 24),
            email=u'myemail@mail.com',
        )
        myTicket.save()
        assert myTicket.ticket_type

        def prioritiseGames():

            form_data = {
                u'csrfmiddlewaretoken': u'igkwDbb97YB4gx44KMHR5kwkziL7Wpql',
                u'priorities-0-id': u'28',
                u'priorities-0-priority': u'0',
                u'priorities-0-ticket': u'18',
                u'priorities-1-id': u'29',
                u'priorities-1-priority': u'0',
                u'priorities-1-ticket': u'18',
                u'priorities-2-id': u'30',
                u'priorities-2-priority': u'0',
                u'priorities-2-ticket': u'18',
                u'priorities-INITIAL_FORMS': u'3',
                u'priorities-MAX_NUM_FORMS': u'1000',
                u'priorities-TOTAL_FORMS': u'3',
                }
