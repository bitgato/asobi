import os
import django

# Initialize the settings before importing consumers etc
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asobi.settings')
django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.urls import path  # noqa: E402
from . import consumers  # noqa: E402

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
