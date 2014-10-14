# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0004_auto_20141014_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemtype',
            name='stars',
            field=models.PositiveSmallIntegerField(help_text='Max stars that participants can give during signup.', default=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='signup',
            name='status',
            field=models.IntegerField(choices=[(1, 'Game Master'), (3, 'Game Host'), (2, 'Participant'), (0, 'Not assigned')], default=0),
        ),
    ]
