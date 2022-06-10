from django.db import models
from django.db.models import Q, F
from .abstract import ClaimingGameSquare, ClaimingGame


class OthelloSquare(ClaimingGameSquare):
    COLORS = [
        ('None', 'None'),
        ('Black', 'Black'),
        ('White', 'White')
    ]
    game = models.ForeignKey('OthelloGame', on_delete=models.CASCADE)
    owner = models.CharField(choices=COLORS, max_length=10, default='None')
    movable = models.BooleanField(default=False)

    @staticmethod
    def check_movable(squares, color, opponent_color):
        # If the first adjacent disc is not the opponent's
        if squares[0].owner != opponent_color:
            return False
        for square in squares:
            owner = square.owner
            if owner == color:
                return True
            if owner == 'None':
                return False
        return False

    @staticmethod
    def flip(squares, color, opponent_color):
        if squares[0].owner != opponent_color:
            return
        can_flip = False
        flipped_squares_pks = []
        for square in squares:
            owner = square.owner
            if owner == opponent_color:
                flipped_squares_pks.append(square.pk)
            elif owner == color:
                # Can only flip if another disc of the player's color is found
                can_flip = True
                break
            else:
                flipped_squares_pks.clear()
                break
        if can_flip and flipped_squares_pks:
            OthelloSquare.objects.filter(pk__in=flipped_squares_pks).update(owner=color)

    def check_adjacent_squares(self, squares, color, flip=False):
        opponent_color = 'White' if color == 'Black' else 'Black'
        game = self.game
        n = game.N
        movable = False

        row = squares.filter(row=self.row)
        column = squares.filter(col=self.col)
        right_diagonal = squares.filter(row=(self.row - self.col) + F('col'))
        left_diagonal = squares.filter(row=(self.row + self.col) - F('col'))

        up = Q(row__lt=self.row)
        down = Q(row__gt=self.row)
        left = Q(col__lt=self.col)
        right = Q(col__gt=self.col)

        operation = self.flip if flip else self.check_movable

        """ Left """
        if self.col >= 2:
            left_squares = row.filter(left).order_by('-col')
            movable = operation(left_squares, color, opponent_color)

        """ Right """
        if (flip or not movable) and (self.col < n - 2):
            right_squares = row.filter(right).order_by('col')
            movable = operation(right_squares, color, opponent_color)

        """ Up """
        if (flip or not movable) and self.row >= 2:
            up_squares = column.filter(up).order_by('-row')
            movable = operation(up_squares, color, opponent_color)

        """ Down """
        if (flip or not movable) and (self.row < n - 2):
            down_squares = column.filter(down).order_by('row')
            movable = operation(down_squares, color, opponent_color)

        """ Top-left """
        if (flip or not movable) and (self.row >= 2) and (self.col >= 2):
            top_left_squares = right_diagonal.filter(up).order_by('-row')
            movable = operation(top_left_squares, color, opponent_color)

        """ Top-right """
        if (flip or not movable) and (self.row >= 2) and (self.col < n - 2):
            top_right_squares = left_diagonal.filter(up).order_by('-row')
            movable = operation(top_right_squares, color, opponent_color)

        """ Bottom-left """
        if (flip or not movable) and (self.row < n - 2) and (self.col >= 2):
            bottom_left_squares = left_diagonal.filter(down).order_by('row')
            movable = operation(bottom_left_squares, color, opponent_color)

        """ Bottom-right """
        if (flip or not movable) and (self.row < n - 2) and (self.col < n - 2):
            bottom_right_squares = right_diagonal.filter(down).order_by('row')
            movable = operation(bottom_right_squares, color, opponent_color)

        if movable:
            self.movable = True
            self.save(update_fields=['movable'])

    def claim_and_get_squares(self, user):
        all_squares = self.game.get_all_squares()
        color = 'Black' if user == self.game.creator else 'White'

        self.check_adjacent_squares(all_squares, color, flip=True)

        self.owner = color
        self.save(update_fields=['owner'])

        all_squares.update(movable=False)

        self.game.creator_pts = all_squares.filter(owner='Black').count()
        self.game.opponent_pts = all_squares.filter(owner='White').count()
        self.game.last_move = self
        self.game.save(update_fields=['creator_pts', 'opponent_pts', 'last_move'])

        self.game.next_player_turn()
        self.game.check_moves(all_squares)

        # If the current turn player has no valid moves
        if not all_squares.filter(movable=True).count():
            self.game.next_player_turn()
            self.game.check_moves(all_squares)
            # If the other player does not have any valid moves either,
            # the game is over and we have to set the winner according to the points
            if not all_squares.filter(movable=True).count():
                if self.game.creator_pts == self.game.opponent_pts:
                    self.game.mark_complete()
                elif self.game.creator_pts > self.game.opponent_pts:
                    self.game.mark_complete(winner=self.game.creator)
                else:
                    self.game.mark_complete(winner=self.game.opponent)

        return all_squares


class OthelloGame(ClaimingGame):
    N = 8
    INITIAL_DISCS = 2
    square_model = OthelloSquare

    creator_pts = models.PositiveIntegerField(default=INITIAL_DISCS)
    opponent_pts = models.PositiveIntegerField(default=INITIAL_DISCS)
    last_move = models.ForeignKey(OthelloSquare, blank=True, null=True, on_delete=models.CASCADE)

    @staticmethod
    def create_new(user):
        new_game = OthelloGame(creator=user, turn=user)
        new_game.save()
        squares = []
        for row in range(new_game.N):
            for col in range(new_game.N):
                square = OthelloSquare(game=new_game, row=row, col=col)
                if (row == 3 and col == 3) or (row == 4 and col == 4):
                    square.owner = 'White'
                if (row == 3 and col == 4) or (row == 4 and col == 3):
                    square.owner = 'Black'
                squares.append(square)
        OthelloSquare.objects.bulk_create(squares)
        new_game.check_moves(new_game.get_all_squares())
        return new_game

    def check_moves(self, all_squares):
        squares = all_squares.filter(owner='None')
        color = 'Black' if self.turn == self.creator else 'White'
        for square in squares:
            square.check_adjacent_squares(all_squares, color)

    def reset(self):
        super(OthelloGame, self).reset()
        self.creator_pts = self.INITIAL_DISCS
        self.opponent_pts = self.INITIAL_DISCS
        self.last_move = None
        self.save(update_fields=['creator_pts', 'opponent_pts', 'last_move'])

        all_squares = self.get_all_squares()
        all_squares.update(owner='None', movable=False)
        squares = [
            self.get_square(row=3, col=4),
            self.get_square(row=4, col=3),
            self.get_square(row=3, col=3),
            self.get_square(row=4, col=4)
        ]
        squares[0].owner = 'Black'
        squares[1].owner = 'Black'
        squares[2].owner = 'White'
        squares[3].owner = 'White'
        OthelloSquare.objects.bulk_update(squares, ['owner'])
        self.check_moves(all_squares)
