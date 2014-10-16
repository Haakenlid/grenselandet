# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0006_auto_20141014_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='staff_only',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
