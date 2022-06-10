import secrets
import string
from django.db import models
from django.db import IntegrityError
from django.contrib.auth.models import User


class Game(models.Model):
    class Meta:
        abstract = True

    GC_LEN = 16  # maximum number of letters in a game_code
    game_code = models.CharField(max_length=GC_LEN, unique=True, editable=False)
    creator = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return f"Game room {self.pk}"

    def generate_game_code(self):
        self.game_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(self.GC_LEN))

    def save(self, *args, **kwargs):
        if not self.game_code:
            self.generate_game_code()
        success = False
        failures = 0
        while not success:
            try:
                super(Game, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise
                else:
                    self.generate_game_code()
            else:
                success = True

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_code(cls, game_code):
        try:
            return cls.objects.get(game_code=game_code)
        except cls.DoesNotExist:
            return None


class ClaimingGameSquare(models.Model):
    class Meta:
        abstract = True

    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()

    @classmethod
    def get_by_id(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None


class ClaimingGame(Game):
    class Meta:
        abstract = True

    square_model = None
    turn = models.ForeignKey(User, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    opponent = models.ForeignKey(User, related_name='+', blank=True, null=True, on_delete=models.CASCADE)

    def next_player_turn(self):
        self.turn = self.creator if self.turn != self.creator else self.opponent
        self.save(update_fields=['turn'])

    def mark_complete(self, winner=None):
        self.completed = True
        if winner is not None:
            self.winner = winner
            self.save(update_fields=['completed', 'winner'])
        else:
            self.save(update_fields=['completed'])

    def set_opponent(self, user):
        self.opponent = user
        self.save(update_fields=['opponent'])

    def get_square(self, row, col):
        try:
            return self.square_model.objects.get(game=self, row=row, col=col)
        except self.square_model.DoesNotExist:
            return None

    def get_all_squares(self):
        return self.square_model.objects.filter(game=self).order_by('id')

    def get_all_players(self):
        return

    def reset(self):
        self.completed = False
        self.turn = self.creator
        self.winner = None
        self.save(update_fields=['completed', 'turn', 'winner'])
        # Overloaded methods in derived classes to reset squares as well
