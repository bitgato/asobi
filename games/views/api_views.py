from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from games.serializers import *


class CurrentUserView(APIView):
    @staticmethod
    def get(request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ClaimingGameViewSet(APIView):
    def __init__(self, game_model, game_serializer, square_serializer):
        super(ClaimingGameViewSet, self).__init__()
        self.game_model = game_model
        self.game_serializer = game_serializer
        self.square_serializer = square_serializer

    # _ is request
    def get(self, _, **kwargs):
        game = self.game_model.get_by_code(kwargs['game_code'])
        if game is None:
            raise Http404
        squares = game.get_all_squares()
        game_serializer = self.game_serializer(game)
        square_serializer = self.square_serializer(squares, many=True)
        return_data = {'game': game_serializer.data,
                       'squares': square_serializer.data}
        return Response(return_data)


class TicTacToeViewSet(ClaimingGameViewSet):
    def __init__(self):
        super(TicTacToeViewSet, self).__init__(
            game_model=TicTacToeGame,
            game_serializer=TicTacToeSerializer,
            square_serializer=TicTacToeSquareSerializer
        )


class ObstructionViewSet(ClaimingGameViewSet):
    def __init__(self):
        super(ObstructionViewSet, self).__init__(
            game_model=ObstructionGame,
            game_serializer=ObstructionSerializer,
            square_serializer=ObstructionSquareSerializer
        )


class LudoViewSet(APIView):
    # _ is request
    @staticmethod
    def get(_, **kwargs):
        game = LudoGame.get_by_code(kwargs['game_code'])
        if game is None:
            raise Http404
        players = game.get_all_players()
        pieces = game.get_all_pieces()
        game_serializer = LudoGameSerializer(game)
        player_serializer = LudoPlayerSerializer(players, many=True)
        piece_serializer = LudoPieceSerializer(pieces, many=True)
        return_data = {'game': game_serializer.data,
                       'players': player_serializer.data,
                       'pieces': piece_serializer.data}
        return Response(return_data)


class BattleshipViewset(APIView):
    # _ is request
    @staticmethod
    def get(_, **kwargs):
        game = BattleshipGame.get_by_code(kwargs['game_code'])
        if game is None:
            raise Http404
        creator_squares = game.get_creator_squares()
        opponent_squares = game.get_opponent_squares()
        game_serializer = BattleshipSerializer(game)
        creator_square_serializer = BattleshipSquareSerializer(creator_squares, many=True)
        opponent_square_serializer = BattleshipSquareSerializer(opponent_squares, many=True)
        data = {
            'game': game_serializer.data,
            'creator_squares': creator_square_serializer.data,
            'opponent_squares': opponent_square_serializer.data
        }
        return Response(data)


class Connect4Viewset(APIView):
    # _ is request
    @staticmethod
    def get(_, **kwargs):
        game = Connect4Game.get_by_code(kwargs['game_code'])
        if game is None:
            raise Http404
        squares = game.get_all_squares()
        game_serializer = Connect4Serializer(game)
        square_serializer = Connect4SquareSerializer(squares, many=True)
        data = {
            'game': game_serializer.data,
            'squares': square_serializer.data
        }
        return Response(data)


class OthelloViewset(APIView):
    # _ is request
    @staticmethod
    def get(_, **kwargs):
        game = OthelloGame.get_by_code(kwargs['game_code'])
        if game is None:
            raise Http404
        squares = game.get_all_squares()
        game_serializer = OthelloSerializer(game)
        square_serializer = OthelloSquareSerializer(squares, many=True)
        data = {
            'game': game_serializer.data,
            'squares': square_serializer.data
        }
        return Response(data)
