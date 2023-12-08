from django.shortcuts import render, get_object_or_404, redirect
from .models import Game
from stats.models import StatsMorpion, StatsWin
from .forms import JoinGameForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def stats_view(request):
    template_name = "morpion/stats.html"
    all_stats = StatsMorpion.objects.all()

    # Créez une liste pour stocker les statistiques formatées
    formatted_stats = []

    # Parcourez chaque statistique et récupérez les informations nécessaires
    for stats in all_stats:
        stats_info = {
            'grid_size': stats.grid_size,
            'alignment': stats.alignment,
            'game_played': stats.game_played,
            'games_won': stats.games_won,
            'winners': StatsWin.objects.filter(stat_morpion=stats).order_by('-wins')[:5],
        }
        formatted_stats.append(stats_info)

    context = {'formatted_stats': formatted_stats}
    return render(request, template_name, context)



def game_over(request, game_id, winner):
    template_name = "morpion/game_over.html"
    game = Game.objects.get(id=game_id)
    game.status = "completed"
    game.save()

    context = {'winner': winner, 'game': game}
    return render(request, template_name, context)

def get_data(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    game_grid = game.get_grid() 

    data = {
        'gameGrid': game_grid, 'gameID': game_id, 'gridSize': game.grid_size, 'activePlayer': game.active_player, 'alignment': game.alignment, 'player2': game.creator.username, 'player2Symbol': game.creator.profile.game_symbol.url
    }
    if(game.player2 != None):
        data['player2'] = game.player2.username
        data['player2Symbol'] = game.player2.profile.game_symbol.url
    return JsonResponse({'data': data})

@csrf_exempt
def update_grid(request, game_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        row = data.get('row')
        col = data.get('col')
        value = data.get('value')
        new_active_player = data.get('newActivePlayer')
        
        try:
            game = Game.objects.get(id=game_id)
            if str(request.user.get_username()) != game.active_player:
                return JsonResponse({'error': 'Vous n\'êtes pas le joueur actif.'})

            game.active_player = str(new_active_player)
            game.save()
            game.update_grid(row, col, value) 

            return JsonResponse({'success': True, 'grid': game.grid})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})

@login_required(login_url='login')
def confirm_join_game(request, game_id):
    template_name ='morpion/game_confirm_join.html'
    game = get_object_or_404(Game, pk=game_id)
    form = JoinGameForm(request.POST or None)

    if request.method == 'POST':
        if 'join' in request.POST:
            if game.status == "waiting":
                if game.player2 is None:
                    if not game.is_private or request.user == game.creator:
                        if game.creator == request.user:
                            return redirect('game-grid', game.id)
                        else:
                            game.player2 = request.user
                            game.status = "started"
                            game.save()
                            return redirect('game-grid', game.id)
                    else:
                        if form.is_valid():
                            access_code = form.cleaned_data['access_code']
                            if access_code == game.access_code:
                                game.player2 = request.user
                                game.status = "started"
                                game.save()
                                return redirect('game-grid', game.id)
                            else:
                                messages.warning(request, 'Code d\'accès incorrect pour la partie privée')
                else:
                    messages.warning(request, 'La partie est déjà pleine')
            else:
                messages.warning(request, 'La partie a déjà commencé ou est terminée')
        elif 'cancel' in request.POST:
            return redirect('/')

    return render(request, template_name, {'game': game, 'form': form})

class GameGridView(View, LoginRequiredMixin):
    template_name = 'morpion/game_grid.html'

    def get(self, request, game_id):
        game = Game.objects.get(pk=game_id)
        player1_image_url = game.creator.profile.game_symbol.url
        game.active_player = game.creator.username
        game.save()
        if game.player2 is not None:
            player2_image_url = game.player2.profile.game_symbol.url
        else:
            player2_image_url = game.creator.profile.game_symbol.url

        game_attributes = json.dumps(game.get_all_attributes())
        context = {
            'game': game,
            'player1_image_url': player1_image_url,
            'player2_image_url': player2_image_url,
            'game_attributes': game_attributes,
        }
        return render(request, self.template_name, context)

class UserGameListView(ListView):
    model = Game
    template_name = 'morpion/user_games.html'
    context_object_name = 'games'
    paginate_by = 3

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Game.objects.filter(creator=user).filter(status="waiting").order_by('-updated_at')

class GameListView(ListView):
    model = Game
    template_name = 'morpion/home.html'
    context_object_name = 'games'
    paginate_by = 3

    def get_queryset(self):
        return Game.objects.filter(status="waiting").order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des parties publiques'
        return context

class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['title', 'grid_size', 'alignment', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        if form.instance.alignment <= form.instance.grid_size:
            if form.instance.is_private:
                form.instance.access_code = Game.generate_access_code(form.instance)                 
            return super().form_valid(form)
        else:
            messages.warning(self.request, 'La taille de la grille doit être plus grande ou égale à l\'alignement !')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('game-grid', args=[self.object.id])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer'
        return context


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    fields = ['title', 'grid_size', 'alignment', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.updated_at = timezone.now() 
        instance = form.save(commit=False)

        if instance.is_private and not instance.access_code:
            instance.access_code = instance.generate_access_code()
        instance.save()
        return super().form_valid(form)

    def test_func(self):
        game = self.get_object()
        if self.request.user == game.creator:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier'
        return context


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    success_url = '/'
    def test_func(self):
        game = self.get_object()
        if self.request.user == game.creator:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer'
        return context


class GameDetailView(DetailView):
    model = Game
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detail de la partie'
        return context