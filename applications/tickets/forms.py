"""
Forms for event registration.
"""
# from django.contrib.auth.models import User
from django import forms
from django.forms.models import inlineformset_factory
from signup.models import Ticket, ActivityPriority
# import datetime
# from paypal.standard.forms import PayPalPaymentsForm
# from paypal.standard.widgets import ValueHiddenInput


class TicketForm(forms.ModelForm):

    """ Initial form to fill out when buying a ticket. """

    class Meta:
        model = Ticket
        fields = [
            'nationality',
            'first_name',
            'last_name',
            'email',
            'date_of_birth',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                "placeholder": "Your first name", "required": "true", }),
            'last_name': forms.TextInput(attrs={
                "placeholder": "Your last name", "required": "true", }),
            'email': forms.EmailInput(attrs={
                "placeholder": "youremail@example.com", "required": "true", }),
            'date_of_birth': forms.DateInput(attrs={
                "placeholder": "YYYY-MM-DD", "pattern": r"^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$",
                "title": "Date of birth (YYYY-MM-DD)", "required": "true", }),
        }


class PriorityForm(forms.ModelForm):

    """Participant chooses which activities to prioritise."""

    # CHOICES = [(num, num) for num in range(1, 4)]
    # priority = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    # priority = forms.ChoiceField(widget=forms.RadioSelect,)

    class Meta:
        model = ActivityPriority
        prefix = 'priority'
        fields = ['priority']
        widgets = {'priority': forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        activity = kwargs['instance'].activity
        self.title = activity.title
        self.creators = activity.creators
        self.description = activity.description
        super(PriorityForm, self).__init__(*args, **kwargs)

PriorityFormSet = inlineformset_factory(
    parent_model=Ticket,
    model=ActivityPriority,
    form=PriorityForm,
    # formset=BaseInlineFormSet,
    # fk_name=None,
    # fields=None,
    # exclude=None,
    extra=0,
    # can_order=False,
    can_delete=False,
    # max_num=None,
    # formfield_callback=None,
    # widgets=None,
    # validate_max=False,
    # localized_fields=None,
    # labels=None,
    # help_texts=None,
    # error_messages=None,
)

# class RegistrationForm(forms.Form):

#     """ Participant registers a new account. """

#     first_name = forms.CharField()
#     last_name = forms.CharField()
#     nationality = forms.ChoiceField(
#         choices=(
#             (u'',
#              u''),
#         ) + NATIONS,
#         widget = forms.Select(
#             attrs={
#                 'data-placeholder': 'Choose a country...',
#                 'class': 'chzn-select',
#                 'style': 'width:190px',
#             }))
#     date_of_birth = forms.DateField(
#         widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
#     date_of_birth.error_messages[
#         'invalid'] = 'Invalid date. Use this format YYYY-MM-DD'
#     email = forms.EmailField(label='Email address')
#     repeat_email = forms.EmailField(label='Confirm email address.')
#     def clean_email(self):
#         """
#         Checks if email is taken.
#         """
#         em1 = self.cleaned_data.get('email')
#         self.clean_email = em1
#         if User.objects.filter(username=em1).exists():
#             raise forms.ValidationError(
#                 'Someone is already registered with that email address')
#         return em1

#     def clean_repeat_email(self):
#         """
#         check if email is identical.
#         """
#         em2 = self.cleaned_data.get('repeat_email')
#         if self.clean_email != em2:
#             raise forms.ValidationError('Emails do not match')

#         return em2
