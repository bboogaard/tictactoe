from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_invite_mail(email: str, session_url: str):
    body = render_to_string('mail/invite.txt', {'session_url': session_url})
    html = render_to_string('mail/invite.html', {'session_url': session_url})
    return send_mail(
        'Join me for a game of TicTacToe',
        message=body,
        from_email=settings.FROM_EMAIL,
        recipient_list=[email],
        html_message=html
    )
