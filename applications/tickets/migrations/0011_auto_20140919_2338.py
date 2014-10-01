# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0010_payment_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_time',
            field=models.DateTimeField(auto_now=True, help_text='Time the ticket was paid.'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(null=True, editable=False, help_text='payment provider transaction id', max_length=50),
        ),
    ]
