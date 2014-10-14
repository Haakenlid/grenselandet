from dajaxice.decorators import dajaxice_register
import json
from .models import ProgramSession, Signup
# from django.contrib.auth.models import User


@dajaxice_register
def change_rating(request):
    # import ipdb; ipdb.set_trace()
    argv = request.POST.get('argv')
    argv = json.JSONDecoder().decode(argv)
    signup = Signup.objects.get(pk=argv['signup_pk'])
    signup.priority = argv['newrating']
    signup.save()
    reply = json.dumps({'success': True})
    return reply
