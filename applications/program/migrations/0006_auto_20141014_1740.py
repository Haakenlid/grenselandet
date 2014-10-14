# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0005_auto_20141014_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programitem',
            name='organisers',
            field=models.ManyToManyField(to='program.Participant', blank=True, related_name='organised_by'),
        ),
    ]
