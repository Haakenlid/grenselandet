# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_auto_20140909_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailtrigger',
            name='trigger',
            field=models.PositiveSmallIntegerField(choices=[(1, 'ticket ordered'), (2, 'ticket paid'), (3, 'ticket cancelled'), (4, 'signup open'), (5, 'signup closed'), (6, 'programme assigned'), (7, 'information')]),
        ),
    ]
