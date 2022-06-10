from .abstract import *
from games.serializers import *


class OthelloConsumer(ClaimingGameConsumer):
    def __init__(self):
        super(OthelloConsumer, self).__init__(
            game_model=OthelloGame,
            square_model=OthelloSquare,
            game_serializer=OthelloSerializer,
            square_serializer=OthelloSquareSerializer,
        )
