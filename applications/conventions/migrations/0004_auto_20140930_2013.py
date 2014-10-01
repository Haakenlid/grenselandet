# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conventions', '0003_convention_place'),
    ]

    operations = [
        migrations.RenameField(
            model_name='convention',
            old_name='place',
            new_name='location',
        ),
    ]
