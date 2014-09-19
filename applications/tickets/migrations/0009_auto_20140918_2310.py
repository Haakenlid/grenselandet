# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_auto_20140918_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
