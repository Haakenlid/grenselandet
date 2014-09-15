# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_auto_20140909_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettype',
            name='status',
            field=models.PositiveSmallIntegerField(default=3, choices=[(0, 'coming_soon'), (1, 'for sale'), (2, 'sold out'), (3, 'secret')]),
            preserve_default=True,
        ),
    ]
