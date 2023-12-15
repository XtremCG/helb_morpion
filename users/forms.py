from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    game_symbol = forms.ImageField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'game_symbol']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.save()

        user.profile.game_symbol = self.cleaned_data['game_symbol']
        user.profile.save()

        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'game_symbol']
