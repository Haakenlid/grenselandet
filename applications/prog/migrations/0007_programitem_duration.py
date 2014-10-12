# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0006_auto_20141012_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='programitem',
            name='duration',
            field=models.PositiveSmallIntegerField(default=240),
            preserve_default=True,
        ),
    ]
