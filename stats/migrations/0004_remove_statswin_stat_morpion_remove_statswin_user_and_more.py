# Generated by Django 4.2.7 on 2023-12-08 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_rename_gris_size_statsmorpion_grid_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statswin',
            name='stat_morpion',
        ),
        migrations.RemoveField(
            model_name='statswin',
            name='user',
        ),
        migrations.DeleteModel(
            name='StatsMorpion',
        ),
        migrations.DeleteModel(
            name='StatsWin',
        ),
    ]
