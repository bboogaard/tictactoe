import random
from typing import Tuple

from django.conf import settings

from tictactoe.exceptions import SlotNotAvailableError
from tictactoe.fields import Symbol
from tictactoe.models import ComputerPlayer, Game, Player


class GameHandler:

    game: Game

    players: Tuple[Player, Player]

    owner_symbol: Symbol

    opponent_symbol: Symbol

    def __init__(self, game: Game):
        self.game = game
        self.players = tuple(self.game.session.players.all())
        self.owner_symbol, self.opponent_symbol = tuple(map(lambda x: Symbol(x), settings.TICTACTOE_PLAYER_SYMBOLS))

    def add_symbol(self, coords: Tuple[int, int]):
        symbol = self.owner_symbol if self.game.active_player == self.game.session.owner else self.opponent_symbol
        x, y = coords
        self.game.board.add_symbol(x, y, symbol)
        self._do_game_checks(self.game.active_player, symbol)
        if not self.game.is_ended:
            try:
                player = self.game.session.computer_player.player
                x, y = self.learn_symbol()
                self.game.board.add_symbol(x, y, self.opponent_symbol)
                self._do_game_checks(player, self.opponent_symbol)
            except ComputerPlayer.DoesNotExist:
                self.game.active_player = next(filter(lambda p: p != self.game.active_player, self.players), None)
        self.game.save()

    def learn_symbol(self) -> Tuple[int, int]:
        for series in self.game.board.get_series():
            if self.game.board.get_series_count(series, self.opponent_symbol) == 2:
                if slot := next(filter(lambda s: s.symbol == Symbol.N, series), None):
                    return slot.coords
        for series in self.game.board.get_series():
            if self.game.board.get_series_count(series, self.owner_symbol) == 2:
                if slot := next(filter(lambda s: s.symbol == Symbol.N, series), None):
                    return slot.coords
        free_slots = [
            slot
            for series in self.game.board.get_series()
            for slot in series
            if slot.symbol == Symbol.N
        ]
        if not free_slots:
            raise SlotNotAvailableError()
        return random.choice(free_slots).coords

    def _do_game_checks(self, player: Player, symbol: Symbol):
        if self.game.board.has_series_complete(symbol):
            self.game.winner = player
            self.game.is_ended = True
        elif self.game.board.is_full:
            self.game.is_ended = True
        self.game.num_symbols += 1


class GameHandlerFactory:

    @classmethod
    def create(cls, game: Game):
        return GameHandler(game)
