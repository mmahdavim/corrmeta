# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-20 00:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtnlss', '0009_auto_20170822_0405'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='isAggregate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variable',
            name='variables',
            field=models.ManyToManyField(related_name='_variable_variables_+', to='mtnlss.Variable'),
        ),
    ]
