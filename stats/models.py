from django.db import models
from morpion.models import Game

class Stats(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"Statistiques pour la partie {self.game.id}"

    @classmethod
    def get_user_activity(cls, user):
        return cls.objects.filter(game__creator=user) | cls.objects.filter(game__player2=user).order_by('game__created_at')