# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-21 04:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import usersystem.models


class Migration(migrations.Migration):

    dependencies = [
        ('usersystem', '0006_auto_20160820_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_password', models.CharField(default='123456', max_length=128)),
                ('sitename', models.CharField(default='example.com:8001', max_length=128)),
                ('start_week_day', models.DateField(default=datetime.date(2016, 9, 4))),
                ('report_editing_day', models.IntegerField(default=7)),
                ('default_head_img', models.ImageField(upload_to=usersystem.models.website_file_upload_path)),
            ],
        ),
    ]
