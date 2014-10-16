# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0007_location_staff_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='programsession',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='signup',
            name='status',
            field=models.IntegerField(choices=[(1, 'Game Master'), (3, 'Preassigned'), (2, 'Participant'), (0, 'Not assigned'), (4, 'Waiting list')], default=0),
        ),
    ]
