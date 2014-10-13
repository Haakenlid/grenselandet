# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0005_auto_20141013_0203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programitem',
            name='organisers',
        ),
    ]
