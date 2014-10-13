# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0004_programsession_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='programitem',
            name='organizers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='organised_by'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='programitem',
            name='organisers',
            field=models.ManyToManyField(to='program.Participant', related_name='organized_by'),
        ),
        migrations.AlterField(
            model_name='programsession',
            name='participants',
            field=models.ManyToManyField(through='program.Signup', blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='signup',
            name='participant',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
