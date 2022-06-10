from .abstract import *
from games.serializers import *


class LudoConsumer(GameConsumer):
    def receive_json(self, content, **kwargs):
        game = LudoGame.get_by_code(self.game_code)

        # if the player is about to roll
        if content['action'] == 'roll':
            player = LudoPlayer.get_by_id(content['player_id'])
            roll = player.dice_roll()
            data = {
                'type': 'run_game',
                'payload': {
                    'roll': roll,
                    'player_id': player.pk
                }
            }
            async_to_sync(self.channel_layer.group_send)(self.group_name, data)
            return

        # if the player's dice roll has finished
        if content['action'] == 'rolled':
            player = LudoPlayer.get_by_id(content['player_id'])

            roll = player.roll
            game.set_cells_to_move(game.cells_to_move + roll)
            if roll < 6:
                player_can_move = player.set_status('Selecting')
                if not player_can_move:
                    game.reset_movement()
                    game.next_player_turn()
            # if player rolled 3 sixes in a row, the turn is passed to the next player
            elif game.cells_to_move == 18:
                game.reset_movement()
                game.next_player_turn()
            # if player rolls a 6, another roll is awarded
            elif roll == 6:
                player.set_status('Rolling')

        # if a piece is moving
        if content['action'] == 'move':
            piece = game.moving_piece
            if 'id' in content:
                piece = LudoPiece.get_by_id(content['id'])
                game.set_moving_piece(piece)

            player = piece.player

            if player.status != 'Moving':
                player.set_status('Moving')
            if game.cells_moved < game.cells_to_move:
                game.set_cells_moved(game.cells_moved + 1)
                piece.move()
            else:
                game.reset_movement()
                piece.set_can_move()
                game.next_player_turn()

        if content['action'] == 'reset':
            game.reset()

        players = game.get_all_players()
        pieces = game.get_all_pieces()

        game_serializer = LudoGameSerializer(game)
        player_serializer = LudoPlayerSerializer(players, many=True)
        piece_serializer = LudoPieceSerializer(pieces, many=True)
        data = {
            'type': 'run_game',
            'payload': {
                'game': game_serializer.data,
                'players': player_serializer.data,
                'pieces': piece_serializer.data
            }
        }
        async_to_sync(self.channel_layer.group_send)(self.group_name, data)
