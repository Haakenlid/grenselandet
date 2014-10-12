# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0007_programitem_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programitem',
            name='description',
            field=models.TextField(help_text='Description of the event'),
        ),
    ]
