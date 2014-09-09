# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('conventions', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sum_paid', models.IntegerField()),
                ('paid_via', models.CharField(help_text='How was the payment made?', max_length=50)),
                ('payment_time', models.DateTimeField(auto_now=True, verbose_name='Time the ticket was paid.')),
            ],
            options={
                'verbose_name_plural': 'Payments',
                'verbose_name': 'Payment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('first_name', models.CharField(null=True, max_length=100)),
                ('last_name', models.CharField(null=True, max_length=100)),
                ('email', models.EmailField(null=True, max_length=75)),
                ('address', models.CharField(help_text='home address', max_length=500)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('date_of_birth', models.DateField(null=True)),
                ('sum_paid', models.PositiveSmallIntegerField(default=0)),
                ('status', models.PositiveSmallIntegerField(help_text='Status of payment.', default=0, choices=[(1, 'ordered'), (2, 'paid'), (0, 'cancelled')])),
                ('order_time', models.DateTimeField(help_text='Time the ticket was ordered', auto_now_add=True)),
                ('comments', models.TextField(blank='True')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketPool',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('max_tickets', models.PositiveSmallIntegerField()),
                ('convention', models.ForeignKey(to='conventions.Convention')),
            ],
            options={
                'verbose_name_plural': 'ticket pools',
                'verbose_name': 'ticket pool',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('price', models.PositiveSmallIntegerField(default=0)),
                ('currency', models.CharField(max_length=3, choices=[('EUR', '€'), ('NOK', 'NOK'), ('USD', 'US $'), ('LTL', 'LTL')])),
                ('max_tickets', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('description', models.CharField(help_text='Short description of the ticket type.', blank=True, max_length=200)),
                ('ticket_pool', models.ForeignKey(to='tickets.TicketPool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_type',
            field=models.ForeignKey(to='tickets.TicketType', related_name='tickets'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='ticket',
            field=models.ForeignKey(to='tickets.Ticket'),
            preserve_default=True,
        ),
    ]
