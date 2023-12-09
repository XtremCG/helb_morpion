# Generated by Django 4.2.7 on 2023-12-09 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('morpion', '0009_alter_game_creator_alter_game_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
