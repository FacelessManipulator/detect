# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-20 04:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import usersystem.models


class Migration(migrations.Migration):

    dependencies = [
        ('usersystem', '0003_report_raw_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attach_file', models.FileField(blank=True, null=True, upload_to=usersystem.models.report_file_upload_path_)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file', to='usersystem.Report')),
            ],
        ),
        migrations.RemoveField(
            model_name='data',
            name='report',
        ),
        migrations.DeleteModel(
            name='Data',
        ),
    ]
