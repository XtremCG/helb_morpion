from django.db import models
from morpion.models import Game

class Stats(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"Statistiques pour la partie {self.game.id}"