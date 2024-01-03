import uuid

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from tictactoe.forms import GameSessionForm, InviteForm, PlayerForm
from tictactoe.mail import send_invite_mail
from tictactoe.models import Game, GameSession, Player
from tictactoe.session import SessionHandlerFactory


class IndexView(TemplateView):

    template_name = 'index.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            game_session = form.save()
            SessionHandlerFactory.create(game_session, request).set('player_id', game_session.owner.player_id)
            return redirect(reverse('tictactoe:session', args=[game_session.session_id]))

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_form(self, data):
        return GameSessionForm(data)


class SessionView(TemplateView):

    template_name = 'session.html'

    def dispatch(self, request, session_id: uuid.UUID, *args, **kwargs):
        self.session = get_object_or_404(GameSession, session_id=session_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        player_id = SessionHandlerFactory.create(self.session, request).get('player_id')
        if player_id:
            return redirect(reverse('tictactoe:session_game', args=[self.session.session_id]))
        elif self.session.is_ready:
            raise Http404()

        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            player = form.save()
            SessionHandlerFactory.create(self.session, request).set('player_id', player.player_id)
            return redirect(reverse('tictactoe:session_game', args=[self.session.session_id]))

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_form(self, data):
        return PlayerForm(data, session=self.session)


class SessionInviteView(TemplateView):

    template_name = 'invite.html'

    def dispatch(self, request, session_id: uuid.UUID, *args, **kwargs):
        self.session = get_object_or_404(GameSession, session_id=session_id)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            send_invite_mail(
                form.cleaned_data['email'],
                request.build_absolute_uri(reverse('tictactoe:session', args=[self.session.session_id]))
            )
            return redirect(reverse('tictactoe:session_game', args=[self.session.session_id]))

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_form(self, data):
        return InviteForm(data)


class SessionGameView(TemplateView):

    template_name = 'game.html'

    def get(self, request, session_id: uuid.UUID, *args, **kwargs):
        session = get_object_or_404(GameSession, session_id=session_id)
        try:
            game = session.game
        except Game.DoesNotExist:
            game = None
        player_id = SessionHandlerFactory.create(session, request).get('player_id')
        player = get_object_or_404(Player, player_id=player_id)
        context = self.get_context_data(
            session=session,
            player=player,
            game=game,
            symbol=settings.TICTACTOE_PLAYER_SYMBOLS[0],
            session_handler_url=reverse('tictactoe:api:session_handler', args=[session.session_id]),
            game_handler_url=reverse('tictactoe:api:game_handler', args=[session.session_id])
        )
        return self.render_to_response(context)
