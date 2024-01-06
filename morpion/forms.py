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
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

    YEAR_CHOICES = [(str(year), str(year)) for year in range(2023, datetime.date.today().year + 1)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, label='Mois', initial=datetime.date.today().month)
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='Année', initial=datetime.date.today().year)

class GameFilterForm(forms.Form):
    grid_size = forms.IntegerField(min_value=1, required=False)
    alignment = forms.IntegerField(min_value=1, required=False)