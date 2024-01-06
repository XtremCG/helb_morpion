from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import random
import string
from django.core.validators import MinValueValidator, MaxValueValidator


class Game(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_created')
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='joined_games')
    active_player = models.CharField(max_length=20, default='')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='games_won')
    abandon = models.CharField(max_length=20, default='', null=True, blank=True)
    title = models.CharField(max_length=200)
    grid_size = models.IntegerField(validators=[MinValueValidator(3), MaxValueValidator(9)])
    alignment = models.IntegerField(validators=[MinValueValidator(3), MaxValueValidator(9)])
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('started', 'Started'),
        ('completed', 'Completed')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    access_code = models.CharField(max_length=6, blank=True, null=True)
    grid_data = models.JSONField(default=dict)
    
    @property
    def grid(self):
        return self.grid_data

    def __str__(self):
        return f"{self.title} ({self.status}) par {self.creator}"

    def get_absolute_url(self):
        return reverse('game-detail', args=[str(self.id)])

    def generate_access_code(self):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return code

    def get_all_attributes(self):
        attributes = {
            'id': self.id,
            'creator': str(self.creator),
            'player2': str(self.player2),
            'active_player': str(self.active_player),
            'title': self.title,
            'grid_size': self.grid_size,
            'alignment': self.alignment,
            'grid': self.grid
        }
        return attributes

    def save(self, *args, **kwargs):
    # Si l'objet est nouveau
        if not self.pk:
            self.grid_data = self.initialize_grid()
    # Si l'objet existe déjà
        elif self.pk:
        # Récupère l'ancienne version de la partie
            old_game = Game.objects.get(pk=self.pk)
        # Vérifie si la taille de la grille a changé
            if self.grid_size != old_game.grid_size:
            # Réinitialise la grille du jeu
                self.grid_data = self.initialize_grid()

        super().save(*args, **kwargs)

    def initialize_grid(self):
        return [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        

    def get_grid(self):
        return self.grid

    def update_grid(self, row, col, value):
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            self.grid_data[row][col] = value
            self.save()