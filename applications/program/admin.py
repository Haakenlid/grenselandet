from django.contrib import admin
from .models import Location, ProgramItem, Signup, ProgramSession, ItemType, Participant

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from django.db.models import Max

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


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
        queryset = queryset.annotate(number_of_signups=Max('signup__priority'))

        if self.value() == 'yes':
            return queryset.exclude(number_of_signups=0)
        if self.value() == 'no':
            return queryset.filter(number_of_signups=0)


class SignupInline(admin.TabularInline):
    model = ProgramSession.participants.through
    fields = ('participant', 'status', 'priority', 'ordering')
    readonly_fields = ('participant',)

    # formset = MyFormSet
    extra = 0


class SessionInline(admin.TabularInline):
    model = ProgramSession

    def admin_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label, instance._meta.module_name), args=[instance.pk]
        )
        return mark_safe(('<a href="{url}">' + instance.__str__() + '</a>').format(url=url))

    extra = 0
    readonly_fields = ('admin_link', 'participants_signed_up', 'game_masters_count')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):

    def signups(obj):
        return obj.signup_set.filter(priority__gt=0).count()

    list_display = ('__str__', 'email', )
    search_fields = ['first_name', 'last_name']
    list_filter = (signed_up_filter,)


@admin.register(ProgramItem)
class ProgramItemAdmin(admin.ModelAdmin):

    # def signups(obj):
    #     return obj.signup_set.filter(priority__gt=0).count()

    # def pri1(obj):
    #     return obj.signup_set.filter(priority=1).count()

    # def pri2(obj):
    #     return obj.signup_set.filter(priority=2).count()

    # def pri3(obj):
    #     return obj.signup_set.filter(priority=3).count()

    save_as = True
    list_display = ('name', 'description', 'item_type', 'duration', 'max_participants', 'sessions')
    list_editable = ('duration', 'max_participants', )
    search_fields = ['name', 'description']
    inlines = [SessionInline, ]
    filter_horizontal = ('organisers',)
    save_on_top = True
    fieldsets = (
        (None,
         {
             'fields': (
                 'name',
                 'description',
                 ('item_type', 'max_participants', 'duration',),
             )
         }
         ),
        ('Organisers',
         {
             'classes': ('collapse',),
             'fields': ('organisers',),
         }
         ),
    )

    def sessions(self, instance):
        return len(instance.programsession_set.all())


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ordering', 'name', 'description', 'max_capacity', 'staff_only', 'convention')
    list_editable = ('ordering', 'name', 'description', 'max_capacity', 'staff_only')


class Priority_filter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('Has signed up')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'hearts'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Yes', ('Signed up')),
            ('No', ('Not signed up')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'Yes':
            return queryset.exclude(priority=0, status=Signup.NOT_ASSIGNED)
        if self.value() == 'No':
            return queryset.filter(priority=0, status=Signup.NOT_ASSIGNED)


@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    search_fields = ('session__programitem__name', 'participant__first_name',
                     'participant__last_name',)
    list_filter = ('status', Priority_filter,)
    list_display = ('id', 'participant', 'session', 'priority', 'status', 'updated',)
    list_editable = ('priority', 'status',)
    fields = (('participant', 'session',), ('priority', 'status', 'updated',))
    readonly_fields = ('updated', )
    save_as = True


def gamemasters(session):
    return session.signup_set.filter(status=Signup.GAME_MASTER).count()


def players(session):
    return session.signup_set.exclude(status=Signup.NOT_ASSIGNED).count()


@admin.register(ProgramSession)
class SessionAdmin(admin.ModelAdmin):
    # __metaclass__ = ForeignKeyLinksMetaclass

    fields = ('programitem',
              ('location',
               'start_time',
               # 'end_time',
               ),
              )

    list_display = (
        'programitem',
        'location',
        'start_time',
        gamemasters,
        players,
        'popularity',
        'participants_signed_up',
    )

    list_editable = ('location', 'start_time',)
    list_filter = ('programitem__item_type',)

    save_on_top = True
    search_fields = ('programitem__name',)
    readonly_fields = ['end_time']

    inlines = [SignupInline, ]


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'color')
