# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Convention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('ticket_sales_opens', models.DateTimeField()),
                ('ticket_sales_closes', models.DateTimeField()),
                ('program_signup_opens', models.DateTimeField()),
                ('program_signup_closes', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Convention',
                'verbose_name_plural': 'Conventions',
            },
            bases=(models.Model,),
        ),
    ]
