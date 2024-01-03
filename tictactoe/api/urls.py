from django.urls import path

from tictactoe.api import views


app_name = 'api'


urlpatterns = [
    path('session-handler/<uuid:session_id>', views.SessionHandlerView.as_view(), name='session_handler'),
    path('game-handler/<uuid:session_id>', views.GameHandlerView.as_view(), name='game_handler'),
]
