# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0008_auto_20141016_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='programsession',
            name='popularity',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
    ]
