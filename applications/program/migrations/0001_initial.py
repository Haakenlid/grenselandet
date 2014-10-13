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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=1000, blank=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=5000, blank=True)),
                ('max_capacity', models.IntegerField(null=True, blank=True)),
                ('ordering', models.IntegerField(default=0)),
                ('convention', models.ForeignKey(to='conventions.Convention', default=applications.program.models.next_convention, related_name='event')),
            ],
            options={
                'ordering': ['ordering', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, help_text='The name of this programme item')),
                ('description', models.TextField(help_text='Description of the event')),
                ('language', models.CharField(default='EN', max_length=2, choices=[('EN', 'English'), ('NO', 'Scandinavian')])),
                ('start_time', models.DateTimeField(default=applications.program.models.next_convention_start_time)),
                ('duration', models.PositiveSmallIntegerField(default=240, help_text='Length in minutes')),
                ('max_participants', models.IntegerField(null=True, blank=True)),
                ('convention', models.ForeignKey(to='conventions.Convention', default=applications.program.models.next_convention)),
                ('item_type', models.ForeignKey(to='program.ItemType')),
                ('location', models.ManyToManyField(to='program.Location', blank=True)),
                ('organisers', models.ManyToManyField(to='program.Participant', blank=True, related_name='organized_by')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.ManyToManyField(to='program.Location', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField(default=0, help_text='chosen by the user')),
                ('status', models.IntegerField(default=0, choices=[(1, 'Game Master'), (2, 'Player'), (0, 'Not assigned')])),
                ('ordering', models.IntegerField(default=0, help_text='Order on the list. To be calculated by an algorithm.')),
                ('participant', models.ForeignKey(to='program.Participant')),
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
            field=models.ManyToManyField(to='program.Participant', through='program.Signup', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='programsession',
            name='programitem',
            field=models.ForeignKey(to='program.ProgramItem'),
            preserve_default=True,
        ),
    ]
