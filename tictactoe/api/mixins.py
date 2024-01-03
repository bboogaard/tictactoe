from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from tictactoe.models import GameSession, Player
from tictactoe.session import SessionHandlerFactory


class GameSessionMixin(APIView):

    @property
    def session(self):
        try:
            return GameSession.objects.get(session_id=self.kwargs['session_id'])
        except GameSession.DoesNotExist:
            raise NotFound()

    @property
    def player(self):
        player_id = SessionHandlerFactory.create(self.session, self.request).get('player_id')
        try:
            return Player.objects.get(player_id=player_id)
        except Player.DoesNotExist:
            raise NotFound()
