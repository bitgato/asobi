import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import QueryDict
from django.contrib import messages
from django.views import View
from games.forms import *


class GameContext:
    def __init__(self, name, url, image, banner=None):
        self.name = name
        self.url = url
        self.image = image
        self.banner = banner


class Home(View):
    template_name = 'home.html'
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    def is_mobile(self, request):
        return self.MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT'])

    def get(self, request):
        is_mobile = self.is_mobile(request)
        ttt_obj = GameContext(
            name='Tic-Tac-Toe',
            url='games:tictactoe',
            image='img/logos/tictactoe.png',
            banner={
                'image': 'img/banners/tictactoe.png' if not is_mobile else 'img/banners/mobile/tictactoe.png',
                'description': 'Probably the most popular pen-and-paper game!'
            })
        obs_obj = GameContext(
            name='Obstruction',
            url='games:obstruction',
            image='img/logos/obstruction.png',
            banner={
                'image': 'img/banners/obstruction.png' if not is_mobile else 'img/banners/mobile/obstruction.png',
                'description': "Don't let your opponent have the last move!"
            })
        ludo_obj = GameContext(
            name='Ludo',
            url='games:ludo',
            image='img/logos/ludo.png',
            banner={
                'image': 'img/banners/ludo.png' if not is_mobile else 'img/banners/mobile/ludo.png',
                'description': 'Race to the finish before others can!'
            }
        )
        battleship_obj = GameContext(
            name='Battleship',
            url='games:battleship',
            image='img/logos/battleship.png',
            banner={
                'image': 'img/banners/battleship.png' if not is_mobile else 'img/banners/mobile/battleship.png',
                'description': "Destroy the enemy fleet before they destroy yours!"
            }
        )
        connect4_obj = GameContext(
            name='Connect Four',
            url='games:connect4',
            image='img/logos/connect4.png',
            banner={
                'image': 'img/banners/connect4.png' if not is_mobile else 'img/banners/mobile/connect4.png',
                'description': 'Connect four in a row before your opponent does!'
            }
        )
        othello_obj = GameContext(
            name='Othello',
            url='games:othello',
            image='img/logos/othello.png',
            banner={
                'image': 'img/banners/othello.png' if not is_mobile else 'img/banners/mobile/othello.png',
                'description': 'A minute to learn, a lifetime to master!'
            }

        )

        context = dict(games=[ttt_obj, obs_obj, ludo_obj, battleship_obj, connect4_obj, othello_obj])

        return render(request, self.template_name, context)


@method_decorator(login_required, name='get')
class GameView(View):
    # All other variables are initialized in child views
    gc = None
    rules_template = None

    def game_redirect(self, request):
        response = redirect(self.page)
        q = QueryDict(mutable=True)
        q['gc'] = self.gc
        response['Location'] += f"?{q.urlencode()}"
        messages.success(request, f"Created new game: {self.gc}")
        return response

    @staticmethod
    def game_obj_operation(request, game_obj):
        if (game_obj.opponent is None) and (game_obj.creator != request.user):
            game_obj.set_opponent(request.user)

    def get(self, request):
        self.gc = request.GET.get('gc')
        context = {'form': self.form_class(), 'rules_template': self.rules_template}
        if self.gc == '':
            # This method is different for all child views, so it is defined later
            self.create_new_game(request)
            return self.game_redirect(request)
        if self.gc:
            try:
                game_obj = self.game_model.objects.get(game_code=self.gc)
                self.game_obj_operation(request, game_obj)
            except self.game_model.DoesNotExist:
                messages.error(request, "No valid game code provided")
                return redirect(self.page)
            context = {'gc': self.gc}
        return render(request, self.template_name, context)


class TicTacToeView(GameView):
    template_name = 'tictactoe.html'
    form_class = StartTicTacToeForm
    game_model = TicTacToeGame
    page = 'games:tictactoe'
    rules_template = 'rules/tictactoe.html'

    def create_new_game(self, request):
        n = request.GET.get('n')
        n = TicTacToeGame.default_n if (n is None) or (n == '') else int(n)
        game = TicTacToeGame.create_new(user=request.user, n=n)
        self.gc = game.game_code


class ObstructionView(GameView):
    template_name = 'obstruction.html'
    form_class = StartObstructionForm
    game_model = ObstructionGame
    page = 'games:obstruction'
    rules_template = 'rules/obstruction.html'

    def create_new_game(self, request):
        rows = request.GET.get('row')
        cols = request.GET.get('col')
        def calc(x): return ObstructionGame.default_n if (x is None) or (x == '') else int(x)
        rows = calc(rows)
        cols = calc(cols)
        game = ObstructionGame.create_new(user=request.user, rows=rows, cols=cols)
        self.gc = game.game_code


class LudoView(GameView):
    template_name = 'ludo.html'
    form_class = StartLudoForm
    game_model = LudoGame
    page = 'games:ludo'
    rules_template = 'rules/ludo.html'

    def create_new_game(self, request):
        players = request.GET.get('players')
        players = 4 if (players is None) or (players == '') else players
        game = LudoGame.create_new(user=request.user, players=players)
        self.gc = game.game_code

    @staticmethod
    def game_obj_operation(request, game_obj):
        game_obj.add_player(request.user)


class BattleshipView(GameView):
    template_name = 'battleship.html'
    form_class = StartBattleShipForm
    game_model = BattleshipGame
    page = 'games:battleship'
    rules_template = 'rules/battleship.html'

    def create_new_game(self, request):
        game = BattleshipGame.create_new(user=request.user)
        self.gc = game.game_code


class Connect4View(GameView):
    template_name = 'connect4.html'
    form_class = StartConnect4Form
    game_model = Connect4Game
    page = 'games:connect4'
    rules_template = 'rules/connect4.html'
    SIZES = {
        '7x6': (7, 6),
        '5x4': (5, 4),
        '6x5': (6, 5),
        '8x7': (8, 7),
        '9x7': (9, 7),
        '10x7': (10, 7),
        '8x8': (8, 8)
    }

    def create_new_game(self, request):
        size = request.GET.get('size')
        size = self.SIZES[size] if size in self.SIZES else (7, 6)
        game = Connect4Game.create_new(user=request.user, size=size)
        self.gc = game.game_code


class OthelloView(GameView):
    template_name = 'othello.html'
    form_class = StartOthelloForm
    game_model = OthelloGame
    page = 'games:othello'
    rules_template = 'rules/othello.html'

    def create_new_game(self, request):
        game = OthelloGame.create_new(user=request.user)
        self.gc = game.game_code
