from django.urls import path
from django.views.generic import TemplateView
from .views import *

app_name = 'games'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('profile/', login_required(ProfileView.as_view()), name='my_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='user_profile'),
    path('games/<str:game_type>/', login_required(GameListView.as_view()), name='my_games_list'),
    path('games/<str:game_type>/<str:username>/', GameListView.as_view(), name='user_games_list'),

    path('tictactoe/', TicTacToeView.as_view(), name='tictactoe'),
    path('obstruction/', ObstructionView.as_view(), name='obstruction'),
    path('ludo/', LudoView.as_view(), name='ludo'),
    path('battleship/', BattleshipView.as_view(), name='battleship'),
    path('connect4/', Connect4View.as_view(), name='connect4'),
    path('othello/', OthelloView.as_view(), name='othello'),

    path('current-user/', CurrentUserView.as_view()),

    path('tictactoe-from-code/<str:game_code>/', TicTacToeViewSet.as_view()),
    path('obstruction-from-code/<str:game_code>/', ObstructionViewSet.as_view()),
    path('ludo-from-code/<str:game_code>/', LudoViewSet.as_view()),
    path('battleship-from-code/<str:game_code>/', BattleshipViewset.as_view()),
    path('connect4-from-code/<str:game_code>/', Connect4Viewset.as_view()),
    path('othello-from-code/<str:game_code>/', OthelloViewset.as_view()),
]
