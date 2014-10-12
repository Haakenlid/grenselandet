# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import applications.prog.models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0002_auto_20141012_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='convention',
            field=models.ForeignKey(to='conventions.Convention', default=applications.prog.models.next_convention, related_name='event'),
        ),
    ]
