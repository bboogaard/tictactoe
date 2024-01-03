from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from tictactoe.api import serializers
from tictactoe.api.mixins import GameSessionMixin
from tictactoe.models import Game


class SessionHandlerView(GameSessionMixin, GenericAPIView):

    serializer_class = serializers.GameSessionSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.session)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            game = self.session.game
            game.is_active = False
            game.save()
        except Game.DoesNotExist:
            ...
        Game.objects.create(
            session=self.session,
            active_player=self.player,
            is_active=True
        )
        return Response(status=status.HTTP_201_CREATED)


class GameHandlerView(GameSessionMixin, GenericAPIView):

    serializer_class = serializers.GameSerializer

    @property
    def game(self):
        try:
            return self.session.game
        except Game.DoesNotExist:
            raise NotFound()

    def get_serializer_context(self):
        return {
            'player': self.player
        }

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.game)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        game_handler_serializer = serializers.GameHandlerSerializer(data=request.data, context={'game': self.game})
        game_handler_serializer.is_valid(raise_exception=True)
        game_handler_serializer.add_symbol()
        serializer = self.get_serializer(instance=self.game)
        return Response(serializer.data)
