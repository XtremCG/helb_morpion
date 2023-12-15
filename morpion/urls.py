from django.urls import path
from . import views
from .views import GameCreateView, GameDetailView, GameUpdateView, GameDeleteView, GameListView, GameGridView, UserGameListView
urlpatterns = [
    path('', GameListView.as_view(), name='morpion-home'),
    path('game/new/', GameCreateView.as_view(), name='game-create'),
    path('game/<int:pk>/detail/', GameDetailView.as_view(), name='game-detail'),
    path('game/<int:pk>/update/', GameUpdateView.as_view(), name='game-update'),
    path('game/<int:pk>/delete/', GameDeleteView.as_view(), name='game-delete'),
    path('confirm-join-game/<int:game_id>/', views.confirm_join_game, name='confirm-join-game'),
    path('game/<int:game_id>/grid/', GameGridView.as_view(), name='game-grid'),
    path('update-grid/<int:game_id>/', views.update_grid, name='update-grid'),
    path('game/<int:game_id>/grid/get-data/', views.get_data, name='get-data'),
    path('game/<int:game_id>/over/<str:winner>/', views.game_over, name='game_over'),
    path('games/user/<str:username>/', UserGameListView.as_view(), name='user-games'),
    path('stats/activity/', views.view_stats_activity, name='activity-stats'),
    path('stats/ranking/', views.view_stats_ranking, name='ranking-stats'),
    path('game/set-abanbon/<int:game_id>/', views.set_abandon, name='set-abandon')

]