from django.shortcuts import render, get_object_or_404, redirect
from .models import Game
from .forms import JoinPrivateGameForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.forms.models import model_to_dict
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

def custom_page_not_found_view(request, exception):
    return render(request, "errors/404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})

def update_active_player(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        if(game.active_player == game.creator):
            game.active_player = game.player2
        elif(game.active_player == game.player2):
            game.active_player = game.creator
        game.save()
        return JsonResponse({'message': 'Attribut mis à jour avec succès.'})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Objet non trouvé.'})


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
            game.active_player = str(new_active_player)
            game.update_grid_value(row, col, value)
            game.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})

def get_attributes(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    game_attributes = json.dumps(game.get_all_attributes())
    if game.player2 is not None:
        player2_symbol = game.player2.profile.game_symbol.url
    player1_symbol = game.creator.profile.game_symbol.url
    print(player1_symbol)
    grid = game.get_grid()

    response_data = {
        'game_attributes': game_attributes,
        'grid': grid,
        'player1_symbol': player1_symbol,
    }

    if game.player2 is not None:
        response_data['player2_symbol'] = player2_symbol
    else :
        response_data['player2_symbol'] = "media/default_symbol.png"

    return JsonResponse(response_data)

def confirm_join_game(request, game_id):
    game = Game.objects.get(pk=game_id)

    if request.method == 'POST':
        if 'join' in request.POST:
            if game.status == "waiting":
                if game.player2 is None:
                    if game.creator == request.user:
                        messages.warning(request, f'Le créateur ne peut pas rejoindre sa propre partie')
                    else:
                        game.player2 = request.user 
                        game.status = "started"
                        game.save()
                        return redirect('game-grid', game.id)
                else:
                    messages.warning(request, f'La partie est déjà pleine')
            else:
                messages.warning(request, f'La partie a déjà commencé')
        elif 'cancel' in request.POST:
            return redirect('/')  

    return render(request, 'morpion/game_public_join.html', {'game': game})

class JoinPrivateGameView(View, LoginRequiredMixin):
    template_name = 'morpion/game_private_join.html'

    def get(self, request):
        form = JoinPrivateGameForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = JoinPrivateGameForm(request.POST)
        if form.is_valid():
            game = form.cleaned_data["game"]
            access_code = form.cleaned_data["access_code"]

            if game.status == "waiting":
                if game.access_code == access_code:
                    if game.player2 is None:
                        if game.creator == request.user:
                            messages.warning(request, f'Le créateur ne peut pas rejoindre sa propre partie')

                        else:
                            game.player2 = request.user
                            game.status = "started"
                            game.save()
                            return redirect('game-grid', game.id)
                    else:
                        messages.warning(request, f'La partie est déjà pleine')
                else:
                    messages.warning(request, f'Code d\'accès incorrect')
            else:
                messages.warning(request, f'La partie a déjà commencée')
        return render(request, self.template_name, {'form': form})


class GameGridView(View, LoginRequiredMixin):
    template_name = 'morpion/game_grid.html'

    def get(self, request, game_id):
        game = Game.objects.get(pk=game_id)
        player1_image_url = game.creator.profile.game_symbol.url
        game.active_player = game.creator
        if game.player2 is not None:
            player2_image_url = game.player2.profile.game_symbol.url
        else:
            player2_image_url = game.creator.profile.game_symbol.url

        game_attributes = json.dumps(game.get_all_attributes())
        game_grid = json.dumps(game.get_grid())
        context = {
            'game': game,
            'player1_image_url': player1_image_url,
            'player2_image_url': player2_image_url,
            'game_attributes': game_attributes,
            'game_grid': game_grid,
        }
        return render(request, self.template_name, context)


class GameListView(ListView):
    model = Game
    template_name = 'morpion/home.html'
    context_object_name = 'games'
    ordering = ['-created_at']

    def get_queryset(self):
        return Game.objects.filter(is_private=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des parties publiques'
        return context


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['title', 'grid_size', 'alignment', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        if form.instance.is_private:
            form.instance.access_code = Game.generate_access_code(form.instance)
        return super().form_valid(form)
    
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