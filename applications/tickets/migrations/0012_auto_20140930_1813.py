# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0011_auto_20140919_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickettype',
            name='description',
            field=models.TextField(help_text='Short description of the ticket type.', blank=True),
        ),
    ]
