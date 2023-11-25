from django import forms
from .models import Game

class JoinPrivateGameForm(forms.Form):
    game = forms.ModelChoiceField(queryset=Game.objects.filter(is_private=True).order_by('-updated_at'), label="Partie privée")
    access_code = forms.CharField(label="Code d'accès")

