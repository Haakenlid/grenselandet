# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0006_remove_programitem_organisers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='programitem',
            old_name='organizers',
            new_name='organisers',
        ),
    ]
