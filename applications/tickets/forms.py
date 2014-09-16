"""
Forms for event registration.
"""
# from django.contrib.auth.models import User
from django import forms
from django.forms.models import inlineformset_factory
from .models import Ticket
# import datetime
# from paypal.standard.forms import PayPalPaymentsForm
# from paypal.standard.widgets import ValueHiddenInput


class TicketForm(forms.ModelForm):

    """ Initial form to fill out when buying a ticket. """

    class Meta:
        model = Ticket
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'email',
            'country',
            'address',
            'city',
            'postal_code',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Your first name',
                'required': 'true',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Your last name',
                'required': 'true',
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Street address',
                'required': 'true',
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City',
                'required': 'true',
            }),
            'postal_code': forms.TextInput(attrs={
                'placeholder': 'Postal Code',
                'required': 'true',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder':
                'youremail@example.com',
                'required': 'true',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'placeholder': 'YYYY-MM-DD',
                'pattern': r'^\d\d\d\d\-\d\d-\d\d',
                'title': 'Date of birth (YYYY-MM-DD)',
                'required': 'true',
            }),
            'country': forms.Select(attrs={
                'class': 'select2',
                'title': 'Country of residence',
                'required': 'true',
            })
        }

    def save(self, *args, **kwargs):
        ticket_type = kwargs.pop('ticket_type')
        kwargs.update(commit=False)
        ticket = super().save(*args, **kwargs)
        ticket.ticket_type = ticket_type
        ticket.save()
        return ticket
