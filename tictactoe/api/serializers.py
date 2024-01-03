from rest_framework import serializers

from tictactoe.api.exceptions import Conflict
from tictactoe.exceptions import TicTacToeException
from tictactoe.game import GameHandlerFactory
from tictactoe.models import Game, GameSession


class GameSessionSerializer(serializers.ModelSerializer):

    is_ready = serializers.SerializerMethodField()

    class Meta:
        model = GameSession
        fields = ('is_ready',)

    def get_is_ready(self, obj):
        return obj.is_ready


class GameSerializer(serializers.ModelSerializer):

    is_active_player = serializers.SerializerMethodField()

    winner = serializers.SerializerMethodField()

    board = serializers.SerializerMethodField()

    scores = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('board', 'num_symbols', 'is_active_player', 'winner', 'is_ended', 'scores')

    @property
    def player(self):
        return self.context.get('player')

    def get_board(self, obj):
        return obj.board.as_list

    def get_is_active_player(self, obj):
        return obj.active_player == self.player

    def get_winner(self, obj):
        return obj.winner.name if obj.winner else None

    def get_scores(self, obj):
        return {
            'owner': obj.session.owner.won_games.count(),
            'opponent': obj.session.opponent.won_games.count(),
        }


class GameHandlerSerializer(serializers.Serializer):

    coords = serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2)

    @property
    def game(self):
        return self.context.get('game')

    def add_symbol(self):
        try:
            GameHandlerFactory.create(self.game).add_symbol(tuple(self.validated_data['coords']))
        except TicTacToeException as exc:
            raise Conflict(str(exc))
