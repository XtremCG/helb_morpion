# Generated by Django 4.2.7 on 2023-12-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('morpion', '0015_alter_game_abandon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='abandon',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
