import secrets
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from .abstract import Game


class LudoPiece(models.Model):
    # 0: red
    # 1: green
    # 2: yellow
    # 3: blue
    # Starting points according to player_number as index
    STARTING_PTS = [2, 15, 28, 41]
    # Separate safe zones marked with a star on the board
    SAFE_ZONES = [49, 10, 23, 36]
    # End column starting points according to player_number as index
    ENDCOL_PREV_PTS = [52, 13, 26, 39]
    ENDCOL_START_PTS = [53, 59, 65, 71]
    HOME_PTS = [58, 64, 70, 76]
    MAX_NORMAL_PT = 52

    game = models.ForeignKey('LudoGame', on_delete=models.CASCADE)
    player = models.ForeignKey('LudoPlayer', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    piece_number = models.PositiveIntegerField()
    can_move = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    @staticmethod
    def create_new(game, player, piece_number):
        LudoPiece(game=game, player=player, piece_number=piece_number).save()

    @staticmethod
    def get_by_id(pk):
        try:
            return LudoPiece.objects.get(pk=pk)
        except LudoPiece.DoesNotExist:
            return None

    def set_back(self):
        self.position = 0
        self.can_move = False
        self.save(update_fields=['position', 'can_move'])

    def is_safe(self):
        """
        Checks if the piece is on a safe zone other than the four star cells
        """
        player_number = self.player.player_number
        endcol_start = self.ENDCOL_START_PTS[player_number]
        home = self.HOME_PTS[player_number]
        is_on_start = self.position == self.STARTING_PTS[player_number]
        is_in_home_col = endcol_start <= self.position <= home
        return is_on_start or is_in_home_col

    def set_can_move(self):
        position = self.position
        player = self.player
        player_number = player.player_number
        cells_to_move = self.game.cells_to_move

        start = self.STARTING_PTS[player_number]
        endcol_prev = self.ENDCOL_PREV_PTS[player_number]
        endcol_start = self.ENDCOL_START_PTS[player_number]
        home = self.HOME_PTS[player_number]

        started = position > 0
        can_start = (position == 0) and (cells_to_move > 6)
        away_from_home = False

        while cells_to_move >= 0:
            final_position = position + cells_to_move
            if final_position > home:
                away_from_home = False
                break
            # Condition 1: If final position is between start point and maximum normal point:
            # position >= start is checked because otherwise it will not take into account
            # the turn into end column
            # Example: For 4th (blue) player, if the position is at 29th cell and the player has
            # to move 17 cells, the final position (29 + 17 = 46) lies between blue's start (41)
            # and maximum normal point (52) but the player should actually not be able to move
            # because the piece will turn to 71th cell after 39th cell. So the player should only
            # be able to move maximum 16 cells from the 29th position
            # Condition 2: If previous condition is false and the final position is less than or
            # equal to the point before end column starts
            # Condition 3: If previous condition is false and the final position is inside the
            # end column or on home
            if (((position >= start) and (start <= final_position <= self.MAX_NORMAL_PT))
                    or (final_position <= endcol_prev)
                    or (endcol_start <= final_position <= home)):
                away_from_home = True
                break
            if final_position > self.MAX_NORMAL_PT:
                # If it's the 1st (red) player, the piece will turn towards 53rd cell
                # (starting point for red's end column), else it will go to 1st cell after
                # passing the 52th (last normal) cell
                position = endcol_start if endcol_prev == self.MAX_NORMAL_PT else 1
                cells_to_move = (final_position - self.MAX_NORMAL_PT) - 1
            elif final_position > endcol_prev:
                # Set final position to start of end column if all the above conditions are
                # false and the final position is after the point before start of end column
                position = endcol_start
                cells_to_move = (final_position - endcol_prev) - 1

        self.can_move = can_start or (started and (not self.finished) and away_from_home)
        self.save(update_fields=['can_move'])

    def move(self):
        position = self.position
        player = self.player
        game = self.game
        player_number = player.player_number

        if self.position == 0:
            game.set_cells_to_move(game.cells_to_move - 6)
            self.position = self.STARTING_PTS[player_number]

        elif position == self.ENDCOL_PREV_PTS[player_number]:
            self.position = self.ENDCOL_START_PTS[player_number]

        elif position == self.MAX_NORMAL_PT:
            self.position = 1

        elif position == self.HOME_PTS[player_number] - 1:
            self.position += 1
            self.finished = True
            self.save(update_fields=['position', 'finished'])
            player.pieces_finished += 1
            if player.pieces_finished == 4:
                game.finished_players += 1
                if game.finished_players == 1:
                    game.winner = player.user
                    game.save(update_fields=['finished_players', 'winner'])
                else:
                    game.save(update_fields=['finished_players'])
                player.position = game.finished_players
                player.save(update_fields=['pieces_finished', 'position'])
            else:
                player.save(update_fields=['pieces_finished'])

        else:
            self.position += 1

        self.save(update_fields=['position'])

        # if the current position is a star safe zone, no need to check for other pieces
        if self.position in self.SAFE_ZONES:
            return

        q1 = Q(game=game)
        q2 = Q(position=self.position)
        q3 = Q(player=self.player)
        # pieces on the same position that do not belong to the same player
        if other_pieces := LudoPiece.objects.filter(q1 & q2 & (~q3)).order_by('id'):
            # set the first such piece back to its house (0 position)
            other_piece = other_pieces[0]
            other_piece.position = 0
            other_piece.can_move = False
            other_piece.save(update_fields=['position', 'can_move'])
            game.reset_movement()

    def reset(self):
        self.position = 0
        self.can_move = False
        self.finished = False
        self.save()


class LudoPlayer(models.Model):
    STATUS_TYPES = (
        ('Waiting', 'Waiting'),
        ('Rolling', 'Rolling'),
        ('Selecting', 'Selecting'),
        ('Moving', 'Moving'),
    )
    game = models.ForeignKey('LudoGame', on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    player_number = models.PositiveIntegerField()
    roll = models.PositiveIntegerField(default=1)
    pieces_finished = models.PositiveIntegerField(default=0)
    status = models.CharField(choices=STATUS_TYPES, max_length=25, default='Waiting')
    position = models.PositiveIntegerField(default=0)

    @staticmethod
    def create_new(game, user, player_number, status='Waiting'):
        new_player = LudoPlayer(game=game, user=user, player_number=player_number, status=status)
        if game.turn == player_number:
            new_player.status = 'Rolling'
        new_player.save()
        for i in range(4):
            LudoPiece.create_new(game=game, player=new_player, piece_number=i)

    @staticmethod
    def get_by_id(pk):
        try:
            return LudoPlayer.objects.get(pk=pk)
        except LudoPlayer.DoesNotExist:
            return None

    def set_status(self, status):
        self.status = status
        player_can_move = False
        if status == 'Selecting':
            for piece in LudoPiece.objects.filter(player=self):
                piece.set_can_move()
                # if even one of the pieces can move, set player_can_move to true
                if (not player_can_move) and piece.can_move:
                    player_can_move = True
        self.save(update_fields=['status'])
        return player_can_move

    def dice_roll(self):
        roll = secrets.choice(range(1, 7))
        self.roll = roll
        self.save(update_fields=['roll'])
        return roll

    def reset(self):
        self.status = 'Rolling' if self.player_number == 0 else 'Waiting'
        self.roll = 1
        self.pieces_finished = 0
        self.position = 0
        self.save()


class LudoGame(Game):
    PLAYER_MODEL = LudoPlayer
    players = models.PositiveIntegerField(default=2)
    finished_players = models.PositiveIntegerField(default=0)
    turn = models.PositiveIntegerField(default=0)
    moving_piece = models.ForeignKey(LudoPiece, blank=True, null=True, on_delete=models.CASCADE)
    cells_to_move = models.PositiveIntegerField(default=0)
    cells_moved = models.PositiveIntegerField(default=0)

    @staticmethod
    def create_new(user, players):
        new_game = LudoGame(creator=user, turn=0, players=players)
        new_game.save()
        # create first player (stored as index 0) and set status to rolling for first turn
        LudoPlayer.create_new(game=new_game, user=user, player_number=0, status='Rolling')
        return new_game

    def add_player(self, user):
        players = self.players
        if LudoPlayer.objects.filter(game=self, user=user):
            return
        for i in range(1, players):
            if not LudoPlayer.objects.filter(game=self, player_number=i):
                LudoPlayer.create_new(game=self, user=user, player_number=i)
                break

    def get_all_players(self):
        return LudoPlayer.objects.filter(game=self).order_by('id')

    def get_all_pieces(self):
        return LudoPiece.objects.filter(game=self).order_by('id')

    def set_moving_piece(self, piece):
        self.moving_piece = piece
        self.save(update_fields=['moving_piece'])

    def set_cells_to_move(self, cells_to_move):
        self.cells_to_move = cells_to_move
        self.save(update_fields=['cells_to_move'])

    def set_cells_moved(self, cells_moved):
        self.cells_moved = cells_moved
        self.save(update_fields=['cells_moved'])

    def reset_movement(self):
        self.set_cells_moved(0)
        self.set_cells_to_move(0)

    def next_player_turn(self):
        # if only a single player is left who hasn't finished, set the game to completed
        # and set the position for the last player according to total number of players
        if (self.finished_players == (self.players - 1)) and (not self.completed):
            for player in self.get_all_players():
                if player.position == 0:
                    player.position = self.players
                    player.save(update_fields=['position'])
                    break
            self.completed = True
            self.turn = 0
            self.save(update_fields=['completed', 'turn'])
            return

        try:
            current_player = LudoPlayer.objects.get(game=self, player_number=self.turn)
        # the current player has not been created yet
        # (first player made his turn and is waiting for others)
        except LudoPlayer.DoesNotExist:
            return
        current_player.set_status('Waiting')
        if self.turn < (self.players - 1):
            self.turn += 1
        else:
            self.turn = 0
        self.save(update_fields=['turn'])
        try:
            next_player = LudoPlayer.objects.get(game=self, player_number=self.turn)
            next_player.set_status('Rolling')
        # The next player has not been created yet
        except LudoPlayer.DoesNotExist:
            pass

    def reset(self):
        self.completed = False
        self.winner = None
        self.moving_piece = None
        self.cells_to_move = 0
        self.cells_moved = 0
        self.turn = 0
        self.finished_players = 0
        self.save()
        for player in self.get_all_players():
            player.reset()
        for piece in self.get_all_pieces():
            piece.reset()
