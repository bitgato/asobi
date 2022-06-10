from .abstract import *
from games.serializers import *


class ObstructionConsumer(ClaimingGameConsumer):
    def __init__(self):
        super(ObstructionConsumer, self).__init__(
            game_model=ObstructionGame,
            square_model=ObstructionSquare,
            game_serializer=ObstructionSerializer,
            square_serializer=ObstructionSquareSerializer,
        )
