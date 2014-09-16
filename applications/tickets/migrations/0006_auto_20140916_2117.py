# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_auto_20140916_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='city',
            field=models.CharField(max_length=500, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='postal_code',
            field=models.CharField(max_length=500, default=''),
            preserve_default=False,
        ),
    ]
