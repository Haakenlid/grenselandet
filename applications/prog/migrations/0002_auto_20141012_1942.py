# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import applications.prog.models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programitem',
            name='start_time',
            field=models.DateTimeField(default=applications.prog.models.next_convention_start_time),
        ),
    ]
