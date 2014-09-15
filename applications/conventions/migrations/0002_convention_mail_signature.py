# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conventions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='convention',
            name='mail_signature',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
