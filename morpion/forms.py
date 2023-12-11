from django import forms

class JoinGameForm(forms.Form):
    access_code = forms.CharField(label="Code d'accès")

class StatsForm(forms.Form):
    alignment = forms.IntegerField(required=False)
    grid_size = forms.IntegerField(required=False)
