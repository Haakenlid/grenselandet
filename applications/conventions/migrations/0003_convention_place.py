# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conventions', '0002_convention_mail_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='convention',
            name='place',
            field=models.CharField(max_length=500, default=''),
            preserve_default=False,
        ),
    ]
