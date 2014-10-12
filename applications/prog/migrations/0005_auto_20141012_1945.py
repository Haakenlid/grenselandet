# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0004_auto_20141012_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programitem',
            name='max_participants',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
