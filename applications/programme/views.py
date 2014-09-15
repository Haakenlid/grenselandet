from django.shortcuts import render

# Create your views here.



class PrioritiesListView(TemplateView):

    """ Show list of games and participants' priorities. """

    template_name = 'priorities-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        priorities = ActivityPriority.objects.filter(
            activity__published=True,
            ticket__activated=True,
            priority__gt=1,
        ).order_by(
            'activity',
            '-priority',
        ).select_related(
            'ticket',
            'activity',
        )
        priorities_by_player = priorities.order_by('ticket', '-priority')
        context['priorities'] = priorities
        context['priorities_by_player'] = priorities_by_player
        return context

class TicketPrioritiseView(DateCheckMixin, TicketMixin, UpdateView, ):
    template_name = 'ticket-prioritise.html'
    form_class = PriorityFormSet
    # inline_model = ActivityPriority
    next_url_label = 'ticket-pay'

    def get_object(self, *args, **kwargs):
        print('get_object',)
        """Return Ticket object based on uuid"""
        # TODO session based version
        ticket = super(TicketPrioritiseView, self).get_object(*args, **kwargs)
        ticket.createPriorities()
        return ticket

    def form_valid(self, form):
        print('form_valid',)
        """ Valid """
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return form_invalid(self, form)
