# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettype',
            name='slug',
            field=models.SlugField(default='slug'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tickettype',
            name='max_tickets',
            field=models.PositiveSmallIntegerField(blank=True, null=True, help_text='only needed if the quota on this ticket type is smaller than the assigned ticket pool.'),
        ),
        migrations.AlterField(
            model_name='tickettype',
            name='ticket_pool',
            field=models.ForeignKey(related_name='ticket_types', to='tickets.TicketPool'),
        ),
    ]
