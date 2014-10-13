# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import applications.program.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('conventions', '0004_auto_20140930_2013'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('color', models.CharField(default='#FFF', max_length=7, help_text='html colour')),
                ('ordering', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['ordering', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=5000)),
                ('max_capacity', models.IntegerField(blank=True, null=True)),
                ('ordering', models.IntegerField(default=0)),
                ('convention', models.ForeignKey(default=applications.program.models.next_convention, related_name='event', to='conventions.Convention')),
            ],
            options={
                'ordering': ['ordering', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('convention', models.ForeignKey(to='conventions.Convention')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='The name of this programme item', max_length=100)),
                ('description', models.TextField(help_text='Description of the event')),
                ('language', models.CharField(max_length=2, choices=[('EN', 'English'), ('NO', 'Scandinavian')], default='EN')),
                ('start_time', models.DateTimeField(default=applications.program.models.next_convention_start_time)),
                ('duration', models.PositiveSmallIntegerField(default=240, help_text='Length in minutes')),
                ('max_participants', models.IntegerField(blank=True, null=True)),
                ('convention', models.ForeignKey(default=applications.program.models.next_convention, to='conventions.Convention')),
                ('item_type', models.ForeignKey(to='program.ItemType')),
                ('location', models.ManyToManyField(blank=True, to='program.Location')),
                ('organisers', models.ManyToManyField(related_name='organised_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramSession',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('start_time', models.DateTimeField(default=applications.program.models.next_convention_start_time)),
                ('location', models.ForeignKey(to='program.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField(default=0, help_text='chosen by the user')),
                ('status', models.IntegerField(default=0, choices=[(1, 'Game Master'), (2, 'Player'), (0, 'Not assigned')])),
                ('ordering', models.IntegerField(default=0, help_text='Order on the list. To be calculated by an algorithm.')),
                ('participant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(to='program.ProgramSession')),
            ],
            options={
                'ordering': ['-status', '-ordering', '-priority'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='signup',
            unique_together=set([('session', 'participant')]),
        ),
        migrations.AddField(
            model_name='programsession',
            name='participants',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, through='program.Signup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programsession',
            name='programitem',
            field=models.ForeignKey(to='program.ProgramItem'),
            preserve_default=True,
        ),
    ]
