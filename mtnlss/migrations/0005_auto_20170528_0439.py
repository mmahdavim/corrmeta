# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-28 04:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtnlss', '0004_paper_variables'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together=set([('project', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='varpaper',
            unique_together=set([('var', 'paper')]),
        ),
    ]
