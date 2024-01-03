from django import forms
import datetime

class JoinGameForm(forms.Form):
    access_code = forms.CharField(label="Code d'accès")

class StatsForm(forms.Form):
    displayed_users = forms.IntegerField(required=True)
    alignment = forms.IntegerField(required=True)
    grid_size = forms.IntegerField(required=True)

class ActivityForm(forms.Form):
    MONTH_CHOICES = [
        ('01', 'Janvier'),
        ('02', 'Février'),
        ('03', 'Mars'),
        ('04', 'Avril'),
        ('05', 'Mai'),
        ('06', 'Juin'),
        ('07', 'Juillet'),
        ('08', 'Août'),
        ('09', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ]

    YEAR_CHOICES = [(str(year), str(year)) for year in range(2023, datetime.date.today().year + 1)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Mois', initial=datetime.date.today().month)
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Année', initial=datetime.date.today().year)