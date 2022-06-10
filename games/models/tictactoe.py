from django.db import models
from .abstract import ClaimingGameSquare, ClaimingGame


class TicTacToeSquare(ClaimingGameSquare):
    game = models.ForeignKey('TicTacToeGame', on_delete=models.CASCADE)
    winning_square = models.BooleanField(default=False)

    def check_winner(self, combination, user, squares, winning_square_pks):
        n = self.game.n
        row = self.row
        col = self.col
        for i in range(n):
            row = row
            col = col
            # Change values of row or col depending upon which winning combination we are looking for
            # For example, in first case, we are looking for a winning row, so we check:
            # all columns (i) in the same row as the square
            if combination == 'row':
                col = i
            elif combination == 'col':
                row = i
            elif combination == 'rdiag':
                row = col = i
            elif combination == 'ldiag':
                row = i
                col = n-1-i
            square = squares.filter(row=row, col=col)[0]
            if square.owner != user:
                winning_square_pks.clear()
                break
            winning_square_pks.append(square.pk)

    def claim_and_get_squares(self, user):
        self.owner = user
        self.save(update_fields=['owner'])

        row = self.row
        col = self.col
        n = self.game.n

        squares = self.game.get_all_squares()
        winning_square_pks = []
        # Check all columns in row of the clicked square
        self.check_winner('row', user, squares, winning_square_pks)

        # Check all rows in column of the clicked square
        if not winning_square_pks:
            self.check_winner('col', user, squares, winning_square_pks)

        # Check right diagonal only if the clicked square lies on it
        if (not winning_square_pks) and (row == col):
            self.check_winner('rdiag', user, squares, winning_square_pks)

        # Check left diagonal only if the clicked square lies on it
        if (not winning_square_pks) and ((row + col) == (n - 1)):
            self.check_winner('ldiag', user, squares, winning_square_pks)

        if winning_square_pks:
            TicTacToeSquare.objects.filter(pk__in=winning_square_pks).update(winning_square=True)
            self.game.mark_complete(winner=user)
        elif not squares.filter(owner=None):
            self.game.mark_complete()
        else:
            self.game.next_player_turn()
        return squares


class TicTacToeGame(ClaimingGame):
    default_n = 3
    square_model = TicTacToeSquare
    n = models.PositiveIntegerField(default=default_n)

    @staticmethod
    def create_new(user, n):
        new_game = TicTacToeGame(creator=user, turn=user, n=n)
        new_game.save()
        squares = []
        for row in range(new_game.n):
            for col in range(new_game.n):
                squares.append(TicTacToeSquare(game=new_game, row=row, col=col))
        TicTacToeSquare.objects.bulk_create(squares)
        return new_game

    def reset(self):
        super(TicTacToeGame, self).reset()
        self.get_all_squares().update(owner=None, winning_square=False)
