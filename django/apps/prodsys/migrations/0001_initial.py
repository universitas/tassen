# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-01 13:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stories', '0022_auto_20161228_0956'),
        ('photo', '0013_imagefile_description'),
        ('contributors', '0010_auto_20151013_2307'),
        ('issues', '0011_data_load_publication_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProdByline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(default=1, help_text='internal ordering of bylines', verbose_name='index')),
                ('credit', models.CharField(choices=[('by', 'by'), ('text', 'text'), ('photo', 'photo'), ('video', 'video'), ('illustration', 'illustration'), ('translation', 'translation'), ('graphics', 'graphics')], default='by', help_text='what this person contributed with', max_length=32, verbose_name='credit')),
                ('description', models.CharField(blank=True, help_text="person's title, qualification or location", max_length=300, verbose_name='description')),
                ('contributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contributors.Contributor')),
            ],
            options={
                'verbose_name': 'ProdByline',
                'verbose_name_plural': 'Bylines',
            },
        ),
        migrations.CreateModel(
            name='ProdImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveSmallIntegerField(default=1, help_text='How prominent this image should be in the layout.', verbose_name='priority')),
                ('position', models.PositiveSmallIntegerField(default=0, help_text='Where this image should be positioned in the layout. 0 is used for header images, other images that should be grouped together should have the same position value', verbose_name='position')),
                ('caption', models.CharField(help_text='caption', max_length=1000, verbose_name='caption')),
                ('image', models.ForeignKey(help_text='image', on_delete=django.db.models.deletion.CASCADE, to='photo.ImageFile', verbose_name='image')),
            ],
            options={
                'verbose_name': 'prodsys image',
                'verbose_name_plural': 'prodsys images',
            },
        ),
        migrations.CreateModel(
            name='ProdStory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(10, 'draft'), (20, 'work in progress'), (30, 'ready for print layout'), (40, 'print layout in progress'), (50, 'ready for web publishing'), (60, 'published on web site'), (90, 'shelved'), (100, 'deleted')], default=10, help_text='status', verbose_name='status')),
                ('working_title', models.CharField(default='new story', help_text='working_title', max_length=200, verbose_name='working_title')),
                ('content', models.TextField(help_text='raw markup content', verbose_name='content')),
                ('comments', models.TextField(help_text='comments', verbose_name='comments')),
                ('issue', models.ForeignKey(help_text='issue', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stories', to='issues.Issue', verbose_name='issue')),
                ('story_type', models.ForeignKey(help_text='story_type', on_delete=django.db.models.deletion.CASCADE, to='stories.StoryType', verbose_name='story_type')),
            ],
            options={
                'verbose_name': 'prodsys story',
                'verbose_name_plural': 'prodsys stories',
                'permissions': [('change_status', 'can change story status')],
            },
        ),
        migrations.CreateModel(
            name='StoryPatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='created', verbose_name='created')),
                ('patch', models.TextField(help_text='patch', verbose_name='patch')),
                ('reverse_patch', models.TextField(default='', help_text='reverse_patch', verbose_name='reverse_patch')),
                ('applied', models.BooleanField(default=False, help_text='applied', verbose_name='applied')),
                ('contributor', models.ForeignKey(default=None, help_text='contributor', null=True, on_delete=django.db.models.deletion.CASCADE, to='contributors.Contributor', verbose_name='contributor')),
                ('story', models.ForeignKey(help_text='story', on_delete=django.db.models.deletion.CASCADE, related_name='patches', to='prodsys.ProdStory', verbose_name='story')),
            ],
        ),
        migrations.AddField(
            model_name='prodimage',
            name='story',
            field=models.ForeignKey(help_text='story', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='prodsys.ProdStory', verbose_name='story'),
        ),
        migrations.AddField(
            model_name='prodbyline',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prodsys.ProdStory'),
        ),
    ]
