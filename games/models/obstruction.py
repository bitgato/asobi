from django.db import models
from .abstract import ClaimingGameSquare, ClaimingGame


class ObstructionSquare(ClaimingGameSquare):
    adjacency_matrix = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if not (i == j == 0)]
    STATUS_TYPES = (
        ('Free', 'Free'),
        ('Selected', 'Selected'),
        ('Surrounding', 'Surrounding')
    )
    game = models.ForeignKey('ObstructionGame', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_TYPES, max_length=25, default='Free')

    def get_surrounding(self):
        results = []
        for dx, dy in self.adjacency_matrix:
            row = self.row + dx
            col = self.col + dy
            if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
                results.append(self.game.get_square(row, col))
        return results

    def claim_and_get_squares(self, user):
        self.owner = user
        self.status = 'Selected'
        self.save(update_fields=['owner', 'status'])

        surrounding = self.get_surrounding()
        for square in surrounding:
            if square.status == 'Free':
                square.owner = user
                square.status = 'Surrounding'
                square.save(update_fields=['owner', 'status'])

        squares = self.game.get_all_squares()
        if squares.filter(status='Free'):
            self.game.next_player_turn()
        else:
            self.game.mark_complete(winner=user)
        return squares


class ObstructionGame(ClaimingGame):
    default_n = 6
    square_model = ObstructionSquare
    rows = models.PositiveIntegerField(default=default_n)
    cols = models.PositiveIntegerField(default=default_n)

    @staticmethod
    def create_new(user, rows, cols):
        new_game = ObstructionGame(creator=user, turn=user, rows=rows, cols=cols)
        new_game.save()
        squares = []
        for row in range(new_game.rows):
            for col in range(new_game.cols):
                squares.append(ObstructionSquare(game=new_game, row=row, col=col))
        ObstructionSquare.objects.bulk_create(squares)
        return new_game

    def reset(self):
        super(ObstructionGame, self).reset()
        self.get_all_squares().update(owner=None, status='Free')
