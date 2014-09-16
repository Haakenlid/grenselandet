# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_tickettype_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='address',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'ordered'), (2, 'paid'), (0, 'cancelled')], help_text='Status of payment.'),
        ),
        migrations.AlterField(
            model_name='tickettype',
            name='status',
            field=models.PositiveSmallIntegerField(default=3, choices=[(0, 'coming soon'), (1, 'for sale'), (2, 'sold out'), (3, 'secret')]),
        ),
    ]
