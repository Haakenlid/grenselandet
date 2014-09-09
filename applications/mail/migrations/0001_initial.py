# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conventions', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('subject', models.TextField()),
                ('body_text', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'mail templates',
                'verbose_name': 'mail template',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTrigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('trigger', models.PositiveSmallIntegerField(choices=[(1, 'ticket ordered'), (2, 'ticket paid'), (3, 'ticket cancelled'), (4, 'signup open'), (5, 'signup closed'), (6, 'programme assigned')])),
                ('convention', models.ForeignKey(to='conventions.Convention', related_name='mailtriggers')),
                ('template', models.ForeignKey(to='mail.MailTemplate', related_name='mailtriggers')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mailtrigger',
            unique_together=set([('convention', 'template', 'trigger')]),
        ),
        migrations.AddField(
            model_name='mailtemplate',
            name='convention',
            field=models.ManyToManyField(to='conventions.Convention', through='mail.MailTrigger', related_name='mail_to_participants'),
            preserve_default=True,
        ),
    ]
