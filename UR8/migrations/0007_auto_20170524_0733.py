# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-24 04:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UR8', '0006_auto_20170510_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='overall',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='video',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
