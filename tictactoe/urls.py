from django.urls import include, path

from tictactoe import views


app_name = 'tictactoe'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<uuid:session_id>', views.SessionView.as_view(), name='session'),
    path('invite/<uuid:session_id>', views.SessionInviteView.as_view(), name='session_invite'),
    path('game/<uuid:session_id>', views.SessionGameView.as_view(), name='session_game'),
    path('api/', include('tictactoe.api.urls', namespace='api')),
]
