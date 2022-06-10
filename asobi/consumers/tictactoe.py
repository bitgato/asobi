from .abstract import *
from games.serializers import *


class TicTacToeConsumer(ClaimingGameConsumer):
    def __init__(self):
        super(TicTacToeConsumer, self).__init__(
            game_model=TicTacToeGame,
            square_model=TicTacToeSquare,
            game_serializer=TicTacToeSerializer,
            square_serializer=TicTacToeSquareSerializer,
        )
