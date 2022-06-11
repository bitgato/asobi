import json
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync


class GameConsumer(JsonWebsocketConsumer):
    def __init__(self):
        super(GameConsumer, self).__init__()
        self.user = None
        self.game_code = None
        # Will append the game code to group-name on connect
        self.group_name = "game-"

    def connect(self):
        self.user = self.scope['user']
        self.game_code = self.scope['url_route']['kwargs']['game_code']
        self.group_name += self.game_code
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, message, **kwargs):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def run_game(self, data):
        self.send(text_data=json.dumps(data['payload']))


class ClaimingGameConsumer(GameConsumer):
    def __init__(self, game_model, square_model, game_serializer, square_serializer):
        super(ClaimingGameConsumer, self).__init__()
        # derived consumer model info
        self.game_model = game_model
        self.square_model = square_model
        self.game_serializer = game_serializer
        self.square_serializer = square_serializer

    def receive_json(self, content, **kwargs):
        game = None
        squares = None
        if content['action'] == 'claim_square':
            square = self.square_model.get_by_id(content['square_id'])
            game = square.game
            squares = square.claim_and_get_squares(self.user)

        if content['action'] == 'reset':
            game = self.game_model.get_by_code(self.game_code)
            game.reset()
            squares = game.get_all_squares()

        game_serializer = self.game_serializer(game)
        square_serializer = self.square_serializer(squares, many=True)
        data = {
            'type': 'run_game',
            'payload': {
                'game': game_serializer.data,
                'squares': square_serializer.data,
            }
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, data)
