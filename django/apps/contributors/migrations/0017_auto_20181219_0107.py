# Generated by Django 2.1.2 on 2018-12-19 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributors', '0016_auto_20180813_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='active',
            field=models.BooleanField(
                default=True, help_text='active', verbose_name='active'
            ),
        ),
        migrations.AlterField(
            model_name='contributor',
            name='display_name',
            field=models.CharField(max_length=50),
        ),
    ]
