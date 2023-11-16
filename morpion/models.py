from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import random, string


class Game(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='joined_games')
    active_player = models.CharField(max_length=20, default=creator)
    title = models.CharField(max_length=200)
    grid_size = models.PositiveIntegerField()
    alignment = models.PositiveIntegerField()
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('started', 'Started'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    access_code = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('game-detail', args=[str(self.id)])

    def generate_access_code(self):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return code

    @property
    def grid(self):
        return [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    
    def get_all_attributes(self):
        attributes = {
            'id': str(self.id),
            'creator': str(self.creator),
            'player2': str(self.player2),
            'active_player': str(self.active_player),
            'title': self.title,
            'grid_size': str(self.grid_size),
            'alignment': str(self.alignment),
            'grid': str(self.grid)
        }
        return attributes

    def get_grid(self):
        return self.grid
    
    def update_grid_value(self, row, col, value):
        self.grid[row][col] = value
        self.save()