from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from .abstract import ClaimingGameSquare, ClaimingGame


class BattleshipSquare(ClaimingGameSquare):
    SHIPS = (
        ('Blank', 'Blank'),
        ('Carrier', 'Carrier'),
        ('Battleship', 'Battleship'),
        ('Cruiser', 'Cruiser'),
        ('Submarine1', 'Submarine1'),
        ('Submarine2', 'Submarine2'),
        ('Destroyer1', 'Destroyer1'),
        ('Destroyer2', 'Destroyer2'),
    )
    DIRECTIONS = (
        ('Row', 'Row'),
        ('Column', 'Column'),
    )
    game = models.ForeignKey('BattleshipGame', on_delete=models.CASCADE)
    attacker = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    ship_piece = models.CharField(choices=SHIPS, max_length=25, default='Blank')
    ship_direction = models.CharField(choices=DIRECTIONS, max_length=15, default='Row')
    is_bow = models.BooleanField(default=False)
    is_aft = models.BooleanField(default=False)
    ship_destroyed = models.BooleanField(default=False)

    def attack(self, user):
        self.attacker = user
        self.save(update_fields=['attacker'])
        if self.ship_piece != 'Blank':
            ship_squares = BattleshipSquare.objects.filter(
                game=self.game,
                owner=self.owner,
                ship_piece=self.ship_piece
            )
            # If all the pieces of this ship has been attacked
            if not ship_squares.filter(attacker=None):
                ship_squares.update(ship_destroyed=True)
                self.game.add_points(user)  # Add points to attacking user

                # q1: same game
                # q2: same owner
                # ~q3: square is not blank (has a ship piece
                # q4: not attacked
                q1 = Q(game=self.game)
                q2 = Q(owner=self.owner)
                q3 = Q(ship_piece='Blank')
                q4 = Q(attacker=None)
                # If all of the other player's ships have been destroyed
                # Only check this if this move destroyed a previously fine ship
                if not BattleshipSquare.objects.filter(q1 & q2 & (~q3) & q4):
                    # Set attacker as winner
                    self.game.mark_complete(winner=user)
        self.game.next_player_turn()


class BattleshipGame(ClaimingGame):
    default_n = 10
    square_model = BattleshipSquare
    creator_confirmed = models.BooleanField(default=False)
    opponent_confirmed = models.BooleanField(default=False)
    creator_points = models.PositiveIntegerField(default=0)
    opponent_points = models.PositiveIntegerField(default=0)

    @staticmethod
    def create_new(user):
        new_game = BattleshipGame(creator=user, turn=user)
        new_game.save()
        squares = []
        for row in range(new_game.default_n):
            for col in range(new_game.default_n):
                squares.append(BattleshipSquare(game=new_game, row=row, col=col, owner=user))
                squares.append(BattleshipSquare(game=new_game, row=row, col=col, owner=None))
        BattleshipSquare.objects.bulk_create(squares)
        return new_game

    def set_opponent(self, user):
        super(BattleshipGame, self).set_opponent(user)
        BattleshipSquare.objects.filter(game=self, owner=None).update(owner=user)

    def add_points(self, attacker):
        if attacker == self.creator:
            self.creator_points += 1
            self.save(update_fields=['creator_points'])
        else:
            self.opponent_points += 1
            self.save(update_fields=['opponent_points'])

    def get_creator_squares(self):
        return BattleshipSquare.objects.filter(game=self, owner=self.creator).order_by('id')

    def get_opponent_squares(self):
        return BattleshipSquare.objects.filter(game=self, owner=self.opponent).order_by('id')

    def confirm(self, user):
        if user == self.creator:
            self.creator_confirmed = True
            self.save(update_fields=['creator_confirmed'])
        else:
            self.opponent_confirmed = True
            self.save(update_fields=['opponent_confirmed'])

    def reset(self):
        super(BattleshipGame, self).reset()
        # Reset other fields of the game
        self.creator_confirmed = False
        self.opponent_confirmed = False
        self.creator_points = 0
        self.opponent_points = 0
        self.save(update_fields=['creator_confirmed', 'opponent_confirmed', 'creator_points', 'opponent_points'])
        # Reset square fields
        self.get_all_squares().update(
            attacker=None,
            ship_piece='Blank',
            ship_direction='Row',
            is_bow=False,
            is_aft=False,
            ship_destroyed=False
        )
