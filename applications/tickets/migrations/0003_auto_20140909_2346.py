# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_auto_20140909_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='hashid',
            field=models.CharField(max_length=100, default='', db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tickettype',
            name='slug',
            field=models.SlugField(editable=False),
        ),
    ]
