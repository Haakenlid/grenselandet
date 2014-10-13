from dajaxice.decorators import dajaxice_register
import json
from .models import ProgramSession, Signup
# from django.contrib.auth.models import User


@dajaxice_register
def change_rating(request):
    # import ipdb; ipdb.set_trace()
    argv = request.POST.get('argv')
    argv = json.JSONDecoder().decode(argv)
    programitem_pk = argv['programitem_pk']
    newrating = argv['newrating']
    u = request.user
    i = ProgramSession.objects.get(pk=programitem_pk)
    a, created = Signup.objects.get_or_create(
        participant=u,
        session=i,
    )
    a.priority = newrating
    a.save()
    r = json.dumps({'success': True})
    return r
