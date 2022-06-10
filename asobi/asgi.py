import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from . import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asobi.settings')

ws_pattern = [
    path('ws/tictactoe/<game_code>', consumers.TicTacToeConsumer.as_asgi()),
    path('ws/obstruction/<game_code>', consumers.ObstructionConsumer.as_asgi()),
    path('ws/ludo/<game_code>', consumers.LudoConsumer.as_asgi()),
    path('ws/battleship/<game_code>', consumers.BattleshipConsumer.as_asgi()),
    path('ws/connect4/<game_code>', consumers.Connect4Consumer.as_asgi()),
    path('ws/othello/<game_code>', consumers.OthelloConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(URLRouter(
        ws_pattern
    ))
})
