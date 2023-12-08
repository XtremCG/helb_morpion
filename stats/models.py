from django.contrib.auth.models import User
from django.db import models

class StatsMorpion(models.Model):
    grid_size = models.IntegerField()
    alignment = models.IntegerField()
    game_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    winners = models.ManyToManyField(User, through='StatsWin')

class StatsWin(models.Model):
    stat_morpion = models.ForeignKey(StatsMorpion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
