from unittest import mock

from django_webtest import WebTest
from django.core import mail
from django.urls import reverse

from tictactoe.game import random
from tictactoe.models import GameSession


class TestViews(WebTest):

    def setUp(self):
        super().setUp()
        self.opponent_app = self.app_class(extra_environ=self.extra_environ)

    def test_all_human_opponent(self):
        response = self.app.get(reverse('tictactoe:index'))
        self.assertEqual(response.status_code, 200)
        form = response.form
        form['name'] = 'My Board'
        form['player_name'] = 'John Doe'
        form['game_mode'] = 'human'
        response = form.submit()
        response = response.follow()
        response = response.follow()
        response.mustcontain('Start game by X')

        session = GameSession.objects.first()
        self.assertIsNotNone(session)

        response = self.app.get(reverse('tictactoe:session_invite', args=[session.session_id]))
        self.assertEqual(response.status_code, 200)
        form = response.form
        form['email'] = 'janedoe@example.org'
        response = form.submit()
        response = response.follow()
        response.mustcontain('Start game by X')

        messages = mail.outbox
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(message.to, ['janedoe@example.org'])
        self.assertIn(reverse('tictactoe:session', args=[session.session_id]), message.body)

        response = self.opponent_app.get(reverse('tictactoe:session', args=[session.session_id]))
        self.assertEqual(response.status_code, 200)
        form = response.form
        form['name'] = 'Jane Doe'
        response = form.submit()
        response = response.follow()
        response.mustcontain('Jane Doe')

        session.refresh_from_db()
        self.assertTrue(session.is_ready)

        response = self.app.post(reverse('tictactoe:api:session_handler', args=[session.session_id]))
        self.assertEqual(response.status_code, 201)

        game = session.game
        self.assertEqual(game.active_player.name, 'John Doe')

        data = {
            'coords': [0, 1]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            [None, 'X', None],
            [None, None, None],
            [None, None, None],
        ])

        data = {
            'coords': [0, 2]
        }
        response = self.opponent_app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            [None, 'X', 'O'],
            [None, None, None],
            [None, None, None],
        ])

        data = {
            'coords': [1, 1]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            [None, 'X', 'O'],
            [None, 'X', None],
            [None, None, None],
        ])

        data = {
            'coords': [1, 2]
        }
        response = self.opponent_app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            [None, 'X', 'O'],
            [None, 'X', 'O'],
            [None, None, None],
        ])

        data = {
            'coords': [2, 1]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            [None, 'X', 'O'],
            [None, 'X', 'O'],
            [None, 'X', None],
        ])
        winner = result['winner']
        self.assertEqual(winner, 'John Doe')

    def test_all_computer_opponent(self):
        response = self.app.get(reverse('tictactoe:index'))
        self.assertEqual(response.status_code, 200)
        form = response.form
        form['name'] = 'My Board'
        form['player_name'] = 'John Doe'
        form['game_mode'] = 'computer'
        response = form.submit()
        response = response.follow()
        response = response.follow()
        response.mustcontain('Start game by X')

        session = GameSession.objects.first()
        self.assertIsNotNone(session)
        self.assertTrue(session.is_ready)

        response = self.app.post(reverse('tictactoe:api:session_handler', args=[session.session_id]))
        self.assertEqual(response.status_code, 201)

        game = session.game
        self.assertEqual(game.active_player.name, 'John Doe')

        def mock_choice_1(slots):
            return slots[0]

        with mock.patch.object(random, 'choice', mock_choice_1):
            data = {
                'coords': [0, 1]
            }
            response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
            self.assertEqual(response.status_code, 200)
            result = response.json
            board = result['board']
            self.assertEqual(board, [
                ['O', 'X', None],
                [None, None, None],
                [None, None, None],
            ])

        data = {
            'coords': [1, 1]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            ['O', 'X', None],
            [None, 'X', None],
            [None, 'O', None],
        ])

        data = {
            'coords': [0, 2]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            ['O', 'X', 'X'],
            [None, 'X', None],
            ['O', 'O', None],
        ])

        data = {
            'coords': [1, 0]
        }
        response = self.app.post_json(reverse('tictactoe:api:game_handler', args=[session.session_id]), data)
        self.assertEqual(response.status_code, 200)
        result = response.json
        board = result['board']
        self.assertEqual(board, [
            ['O', 'X', 'X'],
            ['X', 'X', None],
            ['O', 'O', 'O'],
        ])
        winner = result['winner']
        self.assertEqual(winner, 'Computer')
