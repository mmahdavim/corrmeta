# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-20 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtnlss', '0010_auto_20171120_0034'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variable',
            old_name='isAggregate',
            new_name='isgroup',
        ),
        migrations.AddField(
            model_name='variable',
            name='description',
            field=models.CharField(max_length=3000, null=True),
        ),
    ]
