from django import forms
from .models import Game

class JoinGameForm(forms.Form):
    access_code = forms.CharField(label="Code d'accès")

