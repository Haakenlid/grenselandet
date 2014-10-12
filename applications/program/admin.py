from django.contrib import admin
from .models import Participant, Location, ProgramItem, Signup

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from django.db.models import Max


class nonzero_filter(SimpleListFilter):

    title = _('exclude zero')
    parameter_name = 'nonzero'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(priority=0)
        if self.value() == 'no':
            return queryset.filter(priority=0)


class signed_up_filter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.

    title = _('signed up')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'signedup'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        queryset = queryset.annotate(number_of_signups=Max("signup__priority"))

        if self.value() == 'yes':
            return queryset.exclude(number_of_signups=0)
        if self.value() == 'no':
            return queryset.filter(number_of_signups=0)


class ParticipantAdmin(admin.ModelAdmin):

    def signups(obj):
        return obj.signup_set.filter(priority__gt=0).count()

    def email(obj):
        return obj.user.email
    list_display = ('__str__', 'user', email, signups)
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = (signed_up_filter,)


class ProgramItemAdmin(admin.ModelAdmin):

    def signups(obj):
        return obj.signup_set.filter(priority__gt=0).count()

    def pri1(obj):
        return obj.signup_set.filter(priority=1).count()

    def pri2(obj):
        return obj.signup_set.filter(priority=2).count()

    def pri3(obj):
        return obj.signup_set.filter(priority=3).count()

    list_display = ("name", "language", "start_time", "duration", "end_time", "max_participants", signups, pri1, pri2, pri3)
    list_editable = ("max_participants", "start_time", "duration",)
    filter_horizontal = ("organisers",)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "max_capacity", "convention")
    list_editable = ("name", "description", "max_capacity",)


class SignupAdmin(admin.ModelAdmin):
    list_display = ("id", "participant", "programitem", "priority")
    list_editable = ("programitem", "priority",)
    list_filter = ("programitem", nonzero_filter)


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ProgramItem, ProgramItemAdmin)
admin.site.register(Signup, SignupAdmin)
