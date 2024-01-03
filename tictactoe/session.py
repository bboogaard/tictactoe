from django.http import HttpRequest

from tictactoe.models import GameSession


class SessionHandler:

    KEY_PREFIX: str = 'game-session'

    game_session: GameSession

    request: HttpRequest

    def __init__(self, game_session: GameSession, request: HttpRequest):
        self.game_session = game_session
        self.request = request

    def get(self, item):
        return self.request.session.get(self._make_key(item))

    def set(self, key, value):
        self.request.session[self._make_key(key)] = str(value)

    def _make_key(self, key: str):
        return f'{self.KEY_PREFIX}-{self.game_session.session_id}-{key}'


class SessionHandlerFactory:

    @classmethod
    def create(cls, game_session: GameSession, request: HttpRequest):
        return SessionHandler(game_session, request)
