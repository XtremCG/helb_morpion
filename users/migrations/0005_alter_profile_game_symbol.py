# Generated by Django 4.2.7 on 2023-12-15 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_profile_game_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='game_symbol',
            field=models.ImageField(default='default_symbol.png', upload_to='game_symbols'),
        ),
    ]
