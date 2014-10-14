# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('program', '0002_auto_20141013_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AlterField(
            model_name='programsession',
            name='participants',
            field=models.ManyToManyField(through='program.Signup', blank=True, to='program.Participant'),
        ),
        migrations.AlterField(
            model_name='signup',
            name='participant',
            field=models.ForeignKey(to='program.Participant'),
        ),
    ]
