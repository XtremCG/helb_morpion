from django.shortcuts import render, get_object_or_404, redirect
from .models import Game
from .forms import JoinGameForm, StatsForm
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
from datetime import datetime, timedelta
from django.db.models import Q

def view_stats_ranking(request):
    my_hashmap = {}
    user = request.user
    displayed_users = 3
    alignment = 3
    grid_size = 3
    if request.method == 'POST':
        form = StatsForm(request.POST)
        if form.is_valid():
            alignment = form.cleaned_data['alignment']
            grid_size = form.cleaned_data['grid_size']
            games = Game.objects.filter(Q(alignment=alignment, grid_size=grid_size)).filter(status="completed")
        else:
            games = Game.objects.filter(Q(alignment=alignment, grid_size=grid_size)).filter(status="completed")
    else:
        form = StatsForm()
        games = Game.objects.filter(Q(alignment=alignment, grid_size=grid_size)).filter(status="completed")

    for game in games:
        if game.winner :
            if game.winner in my_hashmap:
                my_hashmap[game.winner] += 1
            else:
                my_hashmap[game.winner] = 1

    users_ranking = dict(sorted(my_hashmap.items(), key=lambda x: x[1], reverse=True))

    top_ranking = dict(list(users_ranking.items())[:displayed_users])

    final_ranking = dict(sorted(top_ranking.items(), key=lambda x: x[1], reverse=True))
    if user:
        user_position = None
        for position, (username, wins) in enumerate(users_ranking.items(), start=1):
            if username == user:
                user_position = position
                break
    if user:    
        user_wins = users_ranking.get(user, 0)

    context = {
        "form": form,
        "final_ranking": final_ranking,
        "user_position": user_position,
        "user_wins": user_wins,
        "displayed_users": displayed_users,
        "alignment": alignment,
        "grid_size": grid_size,
    }
    return render(request, 'morpion/ranking_stats.html', context)

@login_required
def view_stats_activity(request):
    user = request.user
    current_date = datetime.now()

    month = current_date.month
    year = current_date.year
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, 31)

    daily_counter = {}

    for i in range((last_day - first_day).days + 1):
        current_date = first_day + timedelta(days=i)
        games = Game.objects.filter(
            Q(created_at=current_date, creator=user) | Q(created_at=current_date, player2=user)
        ).filter(status="completed")
        daily_counter[current_date.day] = games.count()
    
    context = {
        'x_values': json.dumps(list(daily_counter.keys())),
        'y_values': json.dumps(list(daily_counter.values())),
        'all_zero': all(value == 0 for value in daily_counter.values())
    }
    return render(request, 'morpion/activity_stats.html', context)


def game_over(request, game_id, winner):
    template_name = "morpion/game_over.html"
    game = Game.objects.get(id=game_id)
    game.status = "completed"
    if winner != "Match nul":
        game.winner = User.objects.get(username=winner)
    else :
        game.winner = None
    game.save()

    context = {'winner': winner, 'game': game}
    return render(request, template_name, context)

def get_data(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    game_grid = game.get_grid() 

    data = {
        'abandon':game.abandon ,'gameGrid': game_grid, 'gameID': game_id, 'gridSize': game.grid_size, 'activePlayer': game.active_player, 'alignment': game.alignment, 'player2': game.creator.username, 'player2Symbol': game.creator.profile.game_symbol.url
    }
    if(game.player2 != None):
        data['player2'] = game.player2.username
        data['player2Symbol'] = game.player2.profile.game_symbol.url
        
    if game.abandon is not None:
        user = User.objects.get(username=game.abandon)
        if user != request.user:
            game.winner = request.user
            game.status = "completed"
            messages.warning(request, f'Votre adversaire {user.username} a quitté la partie, vous avez donc gagné la partie.')
    return JsonResponse({'data': data})

@csrf_exempt
def set_abandon(request, game_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        abandon = data.get('abandonPlayer')
        try:
            game = Game.objects.get(id=game_id)
            game.abandon = abandon
            game.status = "completed"
            abandonUser = User.objects.get(username=abandon)
            if abandonUser == game.creator:
                game.winner = game.player2
            elif abandonUser == game.player2:
                game.winner = game.creator
            game.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Invalid request method'})

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
            print(type(request.user.get_username()))
            if str(request.user.get_username()) != game.active_player:
                return JsonResponse({'error': 'Vous n\'êtes pas le joueur actif.'})

            game.active_player = str(new_active_player)
            game.update_grid(row, col, value)

            return JsonResponse({'success': True})
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
        game.save()
        if game.player2 is not None:
            player2_image_url = game.player2.profile.game_symbol.url
        else:
            player2_image_url = game.creator.profile.game_symbol.url

        game_attributes = json.dumps(game.get_all_attributes())
        print(game.grid_size)
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
        form.instance.active_player = self.request.user
        form.instance.winner = None
        form.instance.abandon = None
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
        if self.request.user == game.creator and game.status != 'started':
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