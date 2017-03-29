# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-06 14:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0008_issue_issue_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printissue',
            name='issue',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='pdfs', to='issues.Issue'),
        ),
        migrations.AlterField(
            model_name='printissue',
            name='pdf',
            field=models.FileField(
                help_text='Pdf file for this issue.', upload_to='pdf/'),
        ),
    ]
