from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import random
import string

class Game(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='joined_games')
    active_player = models.CharField(max_length=20, default='')

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
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    access_code = models.CharField(max_length=6, blank=True, null=True)
    grid_data = models.JSONField(default=dict)

    @property
    def grid(self):
        return self.grid_data

    def __str__(self):
        return f"{self.title} ({self.status}) by {self.creator}"

    def get_absolute_url(self):
        return reverse('game-detail', args=[str(self.id)])

    def generate_access_code(self):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return code

    def get_all_attributes(self):
        attributes = {
            'id': str(self.id),
            'creator': str(self.creator),
            'player2': str(self.player2),
            'active_player': str(self.active_player),
            'title': self.title,
            'grid_size': str(self.grid_size),
            'alignment': str(self.alignment)
        }
        return attributes

    def save(self, *args, **kwargs):
        if not self.pk:
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
