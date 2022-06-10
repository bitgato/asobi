from .abstract import *
from games.serializers import *


class BattleshipConsumer(GameConsumer):
    def receive_json(self, content, **kwargs):
        game = None

        if content['action'] == 'confirm':
            game = BattleshipGame.get_by_code(self.game_code)
            squares = []
            for ship, value_dict in content.items():
                if ship == 'action':
                    continue
                direction = value_dict['direction'].capitalize()
                square_id_list = value_dict['squares']
                first = True
                for square_id in square_id_list:
                    square = BattleshipSquare.get_by_id(square_id)
                    square.ship_piece = ship
                    square.ship_direction = direction
                    if first:
                        square.is_bow = True
                        first = False
                    if square_id == square_id_list[-1]:
                        square.is_aft = True
                    squares.append(square)
            BattleshipSquare.objects.bulk_update(squares, ['ship_piece', 'ship_direction', 'is_bow', 'is_aft'])
            game.confirm(self.user)

        if content['action'] == 'attack':
            square = BattleshipSquare.get_by_id(content['square_id'])
            square.attack(self.user)
            game = square.game

        if content['action'] == 'reset':
            game = BattleshipGame.get_by_code(self.game_code)
            game.reset()

        creator_squares = game.get_creator_squares()
        opponent_squares = game.get_opponent_squares()
        game_serializer = BattleshipSerializer(game)
        creator_square_serializer = BattleshipSquareSerializer(creator_squares, many=True)
        opponent_square_serializer = BattleshipSquareSerializer(opponent_squares, many=True)
        data = {
            'type': 'run_game',
            'payload': {
                'game': game_serializer.data,
                'creator_squares': creator_square_serializer.data,
                'opponent_squares': opponent_square_serializer.data
            }
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, data)
