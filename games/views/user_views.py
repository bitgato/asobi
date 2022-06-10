from django.shortcuts import render
from django.http import Http404
from django.views import View
from django.core.paginator import Paginator
from games.models import *


GAMES = {
    'tictactoe': (TicTacToeGame, 'Tic-Tac-Toe', 'img/logos/tictactoe.png'),
    'obstruction': (ObstructionGame, 'Obstruction', 'img/logos/obstruction.png'),
    'ludo': (LudoGame, 'Ludo', 'img/logos/ludo.png'),
    'battleship': (BattleshipGame, 'Battleship', 'img/logos/battleship.png'),
    'connect4': (Connect4Game, 'Connect Four', 'img/logos/connect4.png'),
    'othello': (OthelloGame, 'Othello', 'img/logos/othello.png'),
}


def get_user_from_username(username, request):
    user = None
    if username is None:
        if request.user.is_authenticated:
            user = request.user
    else:
        user = User.objects.filter(username=username)
        if user:
            user = user[0]
    return user


def get_games(game_model, user, last_n=None):
    if hasattr(game_model, 'opponent'):
        q1 = Q(creator=user)
        q2 = Q(opponent=user)
        games = game_model.objects.filter(q1 | q2).order_by('-id')
    else:
        user_players = game_model.PLAYER_MODEL.objects.filter(user=user).order_by('-id')
        games = [player.game for player in user_players]
    return games[:last_n] if last_n else games


def get_games_data(games, user, game_type):
    result = []
    for game in games:
        players = game.get_all_players()
        if not players:
            opponent = game.opponent if game.creator == user else game.creator
            players = [opponent] if opponent is not None else []
        else:
            players = [player.user.username for player in players if player.user != user]
        game_data = {
            'game': game,
            'players': players,
            'url': f"/{game_type}/?gc={game.game_code}",
        }
        result.append(game_data)
    return result


class ProfileView(View):
    LAST_N = 5
    template_name = 'profile.html'

    def get(self, request, username=None):
        user = get_user_from_username(username, request)
        if not user:
            raise Http404
        all_games_data = []
        for game_type, values in GAMES.items():
            game_model, display_name, logo = values
            last_n_games = get_games(game_model, user, self.LAST_N)
            game_model_data = get_games_data(last_n_games, user, game_type)
            all_games_data.append({
                'game_type': game_type,
                'display_name': display_name,
                'logo': logo,
                'page_url': f"games:{game_type}",
                'game_model_data': game_model_data,
            })
        context = {'profile_user': user, 'all_games_data': all_games_data}
        return render(request, self.template_name, context)


class GameListView(View):
    PER_PAGE = 25
    template_name = 'games_list.html'

    def get(self, request, game_type=None, username=None):
        if game_type not in GAMES:
            raise Http404
        user = get_user_from_username(username, request)
        if not user:
            raise Http404
        game_model, display_name, logo = GAMES[game_type]
        games = get_games(game_model, user)
        game_model_data = get_games_data(games, user, game_type)
        paginator = Paginator(game_model_data, self.PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'profile_user': user,
            'display_name': display_name,
            'logo': logo,
            'page_url': f"games:{game_type}",
            'page_obj': page_obj
        }
        return render(request, self.template_name, context)
