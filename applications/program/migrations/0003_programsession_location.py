# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0002_remove_programsession_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='programsession',
            name='location',
            field=models.ForeignKey(default=None, to='program.Location'),
            preserve_default=False,
        ),
    ]
