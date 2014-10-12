# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0005_auto_20141012_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='max_capacity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
