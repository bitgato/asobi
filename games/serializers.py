from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class TicTacToeSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    opponent = UserSerializer()
    turn = UserSerializer()

    class Meta:
        model = TicTacToeGame
        fields = ('id', 'winner', 'creator', 'opponent', 'n', 'completed', 'turn')
        depth = 1


class TicTacToeSquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicTacToeSquare
        fields = ('id', 'owner', 'row', 'col', 'winning_square')


class ObstructionSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    opponent = UserSerializer()
    turn = UserSerializer()

    class Meta:
        model = ObstructionGame
        fields = ('id', 'winner', 'creator', 'opponent', 'rows', 'cols', 'completed', 'turn')
        depth = 1


class ObstructionSquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObstructionSquare
        fields = ('id', 'owner', 'row', 'col', 'status')


class LudoGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LudoGame
        fields = ('id', 'players', 'turn', 'completed')
        depth = 1


class LudoPlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = LudoPlayer
        fields = ('id', 'user', 'player_number', 'roll', 'pieces_finished', 'status', 'position')
        depth = 1


class LudoPiecePlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = LudoPlayer
        fields = ('user', 'player_number', 'status')
        depth = 1


class LudoPieceSerializer(serializers.ModelSerializer):
    player = LudoPiecePlayerSerializer()

    class Meta:
        model = LudoPiece
        fields = ('id', 'player', 'position', 'piece_number', 'can_move', 'finished')
        depth = 1


class BattleshipSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    opponent = UserSerializer()
    turn = UserSerializer()

    class Meta:
        model = BattleshipGame
        fields = ('id', 'creator', 'opponent', 'turn', 'completed', 'winner',
                  'creator_confirmed', 'opponent_confirmed', 'creator_points', 'opponent_points')
        depth = 1


class BattleshipSquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleshipSquare
        fields = ('id', 'owner', 'row', 'col', 'attacker', 'ship_piece', 'ship_direction',
                  'is_bow', 'is_aft', 'ship_destroyed')


class Connect4Serializer(serializers.ModelSerializer):
    creator = UserSerializer()
    opponent = UserSerializer()
    turn = UserSerializer()

    class Meta:
        model = Connect4Game
        fields = ('id', 'winner', 'creator', 'opponent', 'rows', 'cols', 'completed', 'turn')
        depth = 1


class Connect4SquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connect4Square
        fields = ('id', 'owner', 'row', 'col', 'winning_square')


class OthelloSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    opponent = UserSerializer()
    turn = UserSerializer()

    class Meta:
        model = OthelloGame
        fields = ('id', 'creator', 'opponent', 'turn', 'completed', 'winner',
                  'last_move', 'creator_pts', 'opponent_pts')
        depth = 1


class OthelloSquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = OthelloSquare
        fields = ('id', 'owner', 'row', 'col', 'movable')
