# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mailtrigger',
            unique_together=set([('convention', 'trigger')]),
        ),
    ]
