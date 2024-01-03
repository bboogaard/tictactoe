from django.db import models

from tictactoe.fields import BoardField, SymbolField


class GameSession(models.Model):

    name = models.CharField(max_length=100)

    session_id = models.UUIDField(unique=True)

    session_time = models.DateTimeField(auto_now=True)

    players = models.ManyToManyField('tictactoe.Player', related_name='sessions', through='tictactoe.SessionPlayer')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def owner(self):
        return self.player_session.get(owner=True).player

    @property
    def opponent(self):
        try:
            player = self.computer_player
        except ComputerPlayer.DoesNotExist:
            try:
                player = self.player_session.get(owner=False)
            except Player.DoesNotExist:
                player = None
        return player.player

    @property
    def game(self):
        return self.games.get(is_active=True)

    @property
    def is_ready(self):
        try:
            computer_player = self.computer_player
        except ComputerPlayer.DoesNotExist:
            computer_player = None
        return self.players.count() == 2 or computer_player


class Player(models.Model):

    name = models.CharField(max_length=100)

    player_id = models.UUIDField(unique=True)

    symbol = SymbolField()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ComputerPlayer(models.Model):

    session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='computer_player')

    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='+')

    class Meta:
        ordering = ('session',)

    def __str__(self):
        return self.player.name


class SessionPlayer(models.Model):

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='player_session')

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='session_player')

    owner = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('session', 'player'),
                name='Unique index on session and player'
            ),
            models.UniqueConstraint(
                fields=('session', 'owner'),
                name='Unique index on session and owner',
                condition=models.Q(owner=True)
            )
        ]

    def __str__(self):
        return f'{self.session} - {self.player}'


class Game(models.Model):

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='games')

    game_time = models.DateTimeField(auto_now=True)

    board = BoardField()

    num_symbols = models.PositiveIntegerField(default=0)

    active_player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL, related_name='games')

    winner = models.ForeignKey(Player, null=True, on_delete=models.CASCADE, related_name='won_games')

    is_active = models.BooleanField(default=False)

    is_ended = models.BooleanField(default=False)

    class Meta:
        ordering = ("session", "-game_time")
        constraints = [
            models.UniqueConstraint(
                fields=('session', 'is_active'),
                name='Unique constraint on session and is_active',
                condition=models.Q(is_active=True)
            )
        ]

    def __str__(self):
        return f'{self.session} - {self.game_time}'
