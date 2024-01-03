import uuid

from django.conf import settings
from django import forms

from tictactoe.fields import Symbol
from tictactoe import models


class GameSessionForm(forms.ModelForm):

    player_name = forms.CharField()

    game_mode = forms.ChoiceField(choices=(
        ('human', 'Human opponent'),
        ('computer', 'Computer')
    ))

    class Meta:
        model = models.GameSession
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.session_id = uuid.uuid4()
        instance.save()
        symbol = Symbol(settings.TICTACTOE_PLAYER_SYMBOLS[0])
        player = models.Player.objects.create(
            name=self.cleaned_data['player_name'],
            player_id=uuid.uuid4(),
            symbol=symbol
        )
        models.SessionPlayer.objects.create(session=instance, player=player, owner=True)
        if self.cleaned_data['game_mode'] == 'computer':
            symbol = Symbol(settings.TICTACTOE_PLAYER_SYMBOLS[1])
            player = models.Player.objects.create(
                name='Computer',
                player_id=uuid.uuid4(),
                symbol=symbol
            )
            models.ComputerPlayer.objects.create(
                session=instance,
                player=player
            )
        return instance


class InviteForm(forms.Form):

    email = forms.EmailField()


class PlayerForm(forms.ModelForm):

    class Meta:
        model = models.Player
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.session = self.session
        instance.player_id = uuid.uuid4()
        instance.symbol = Symbol(settings.TICTACTOE_PLAYER_SYMBOLS[1])
        instance.save()
        models.SessionPlayer.objects.create(session=self.session, player=instance)
        return instance
