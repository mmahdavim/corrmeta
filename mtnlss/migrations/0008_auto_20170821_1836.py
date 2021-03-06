# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-21 18:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtnlss', '0007_auto_20170821_0301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='value',
            field=models.CharField(blank=True, max_length=540, null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='authors',
            field=models.CharField(blank=True, max_length=540, null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='publication',
            field=models.CharField(blank=True, max_length=540, null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='title',
            field=models.CharField(max_length=540),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=540),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.CharField(max_length=540),
        ),
        migrations.AlterField(
            model_name='variable',
            name='name',
            field=models.CharField(max_length=540),
        ),
    ]
