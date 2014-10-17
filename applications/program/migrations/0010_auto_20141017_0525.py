# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0009_programsession_popularity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='status',
            field=models.IntegerField(default=0, choices=[(1, 'Game Master'), (3, 'Preassigned'), (4, 'Volunteer'), (2, 'Participant'), (0, 'Not assigned'), (5, 'Waiting list')]),
        ),
    ]
