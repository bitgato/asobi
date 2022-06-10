from django.db import models
from django.db.models import F
from .abstract import ClaimingGame, ClaimingGameSquare


class Connect4Square(ClaimingGameSquare):
    game = models.ForeignKey('Connect4Game', on_delete=models.CASCADE)
    winning_square = models.BooleanField(default=False)


class Connect4Game(ClaimingGame):
    square_model = Connect4Square
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()

    @staticmethod
    def create_new(user, size):
        # 7x6 is 7 columns and 6 rows
        cols, rows = size
        new_game = Connect4Game(creator=user, turn=user, rows=rows, cols=cols)
        new_game.save()
        squares = []
        for row in range(rows):
            for col in range(cols):
                squares.append(Connect4Square(game=new_game, row=row, col=col))
        Connect4Square.objects.bulk_create(squares)
        return new_game

    @staticmethod
    def check_winner(squares, user, winning_square_pks):
        connected = 0
        for square in squares:
            if square.owner == user:
                winning_square_pks.append(square.pk)
                connected += 1
                if connected == 4:
                    break
            else:
                connected = 0
        if connected < 4:
            winning_square_pks.clear()

    def drop_stone_and_get_squares(self, user, col):
        # Get last available square in column
        drop_square = Connect4Square.objects.filter(game=self, owner=None, col=col).order_by('-row')[0]
        drop_row = drop_square.row
        drop_square.owner = user
        drop_square.save(update_fields=['owner'])

        squares = self.get_all_squares()
        winning_square_pks = []

        # Check column
        column = squares.filter(col=col).order_by('row')
        self.check_winner(column, user, winning_square_pks)

        if not winning_square_pks:
            # Check row
            row = squares.filter(row=drop_row).order_by('col')
            self.check_winner(row, user, winning_square_pks)

        if not winning_square_pks:
            # For all squares in the left diagonal, the sum of 'row' and 'col' will be equal
            # to that of the square where the stone has been dropped
            # Example: (0,3) (1,2) (2,1) (3,0) all lie on the same diagonal
            right_diagonal = squares.filter(row=(drop_row + col) - F('col')).order_by('row')
            self.check_winner(right_diagonal, user, winning_square_pks)

        if not winning_square_pks:
            # For all squares in the left diagonal, the difference between 'row' and 'col' will be equal
            # to that of the square where the stone has been dropped
            # Example: (0,2) (1,3) (2,4) (3,5) (4,6) all lie on the same diagonal
            left_diagonal = squares.filter(row=(drop_row - col) + F('col')).order_by('row')
            self.check_winner(left_diagonal, user, winning_square_pks)

        if winning_square_pks:
            Connect4Square.objects.filter(pk__in=winning_square_pks).update(winning_square=True)
            self.mark_complete(winner=user)
        elif not squares.filter(owner=None):
            self.mark_complete()
        else:
            self.next_player_turn()
        return squares

    def reset(self):
        super(Connect4Game, self).reset()
        self.get_all_squares().update(owner=None, winning_square=False)
