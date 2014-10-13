# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import applications.program.models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0003_programsession_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='programsession',
            name='start_time',
            field=models.DateTimeField(default=applications.program.models.next_convention_start_time),
            preserve_default=True,
        ),
    ]
