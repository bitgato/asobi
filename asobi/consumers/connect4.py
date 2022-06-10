from .abstract import *
from games.serializers import *


class Connect4Consumer(GameConsumer):
    def receive_json(self, content, **kwargs):
        game = Connect4Game.get_by_code(self.game_code)
        squares = None

        if content['action'] == 'drop':
            col = content['col']
            squares = game.drop_stone_and_get_squares(user=self.user, col=col)

        if content['action'] == 'reset':
            game.reset()
            squares = game.get_all_squares()

        game_serializer = Connect4Serializer(game)
        square_serializer = Connect4SquareSerializer(squares, many=True)
        data = {
            'type': 'run_game',
            'payload': {
                'game': game_serializer.data,
                'squares': square_serializer.data
            }
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, data)
