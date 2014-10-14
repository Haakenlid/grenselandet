# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0003_auto_20141014_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programitem',
            name='organisers',
            field=models.ManyToManyField(to='program.Participant', related_name='organised_by'),
        ),
    ]
