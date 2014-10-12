# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('conventions', '0004_auto_20140930_2013'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=5000, blank=True)),
                ('max_capacity', models.IntegerField(blank=True)),
                ('convention', models.ForeignKey(to='conventions.Convention', related_name='event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, help_text='The name of this programme item')),
                ('description', models.CharField(max_length=5000, help_text='Description of the event', null=True)),
                ('itemtype', models.CharField(max_length=20, choices=[('Larp', 'Larp'), ('Freeform', 'Freeform game'), ('Workshop', 'Workshop'), ('Lecture', 'Lecture'), ('Social', 'Social event'), ('Other', 'Other')], default='Larp')),
                ('language', models.CharField(max_length=2, choices=[('EN', 'English'), ('NO', 'Scandinavian')], default='EN')),
                ('start_time', models.DateTimeField()),
                ('max_participants', models.IntegerField(blank=True)),
                ('convention', models.ForeignKey(to='conventions.Convention')),
                ('location', models.ManyToManyField(blank=True, to='prog.Location')),
                ('organisers', models.ManyToManyField(blank=True, to='prog.Participant', related_name='organized_by')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('signup_time', models.DateField(auto_now=True)),
                ('priority', models.IntegerField(default=0)),
                ('participant', models.ForeignKey(to='prog.Participant')),
                ('programitem', models.ForeignKey(to='prog.ProgramItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='programitem',
            name='participants',
            field=models.ManyToManyField(through='prog.Signup', blank=True, to='prog.Participant'),
            preserve_default=True,
        ),
    ]
