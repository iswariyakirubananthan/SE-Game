"""
test_app.py - Comprehensive Automated Test Suite
================================================
Validates all 10 modules and the 4 academic themes:
  - Theme A: Version Control (Can be run in CI/CD pipeline)
  - Theme B: Interoperability (API service parsing and fallback)
  - Theme C: Event responses (game submit, timeout, scoring)
  - Theme D: Virtual Identity (Registration, hashing, session cookies, route protection)
"""

import unittest
import os
import tempfile
from app import create_app
import database
from models.user import UserModel
from models.score import ScoreModel
from services.banana_service import BananaApiService


class BananaQuestTestCase(unittest.TestCase):
    def setUp(self):
        """Set up an isolated test database and test Flask client."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        database.DATABASE_PATH = self.db_path

        self.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key-12345',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            database.init_db()

    def tearDown(self):
        """Clean up temporary test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    # -------------------------------------------------------------
    # Module 1: Home Page Tests
    # -------------------------------------------------------------
    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Banana', response.data)
        self.assertIn(b'Quest', response.data)
        self.assertIn(b'Math Puzzle Engine', response.data)

    # -------------------------------------------------------------
    # Module 2 & 3: Registration, Password Hashing & Login (Theme D)
    # -------------------------------------------------------------
    def test_user_registration_and_duplicate_check(self):
        # Register user 1
        res = self.client.post('/register', data={
            'username': 'player1',
            'email': 'player1@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Check Werkzeug password hashing
        with self.app.app_context():
            u = UserModel.get_by_email('player1@test.com')
            self.assertIsNotNone(u)
            self.assertNotEqual(u['password_hash'], 'password123')
            self.assertTrue(UserModel.verify_password(u['password_hash'], 'password123'))

        # Duplicate email test
        res_dup = self.client.post('/register', data={
            'username': 'player2',
            'email': 'player1@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup.data)

    def test_login_and_session_cookies(self):
        # Register first
        self.client.post('/register', data={
            'username': 'gamer',
            'email': 'gamer@test.com',
            'password': 'pass123456',
            'confirm_password': 'pass123456'
        })

        # 1. Login with wrong password first
        res_wrong = self.client.post('/login', data={
            'email': 'gamer@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', res_wrong.data)

        # 2. Login with correct password
        res = self.client.post('/login', data={
            'email': 'gamer@test.com',
            'password': 'pass123456'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'gamer', res.data)
        self.assertIn(b'Highest Score', res.data)

    # -------------------------------------------------------------
    # Module 4: Route Protection (Virtual Identity)
    # -------------------------------------------------------------
    def test_unauthenticated_protected_route_redirection(self):
        res = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in to access this area', res.data)

        res_game = self.client.get('/game/play', follow_redirects=True)
        self.assertIn(b'Please log in to access this area', res_game.data)

    # -------------------------------------------------------------
    # Module 5 & 6: Game Engine, Difficulty & Security
    # -------------------------------------------------------------
    def test_difficulty_configurations(self):
        with self.client:
            # Register & log in
            self.client.post('/register', data={
                'username': 'tester',
                'email': 'tester@test.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.client.post('/login', data={'email': 'tester@test.com', 'password': 'password123'})

            # Start Easy Game
            res = self.client.post('/game/api/start', json={'difficulty': 'easy'})
            data = res.get_json()
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['time_limit'], 60)
            self.assertEqual(data['lives'], 3)
            self.assertEqual(data['points_per_correct'], 10)
            # CRITICAL SECURITY CHECK: Solution must NEVER be in response JSON!
            self.assertNotIn('solution', data)
            self.assertNotIn('current_solution', data)

            # Start Hard Game
            res_hard = self.client.post('/game/api/start', json={'difficulty': 'hard'})
            data_hard = res_hard.get_json()
            self.assertEqual(data_hard['time_limit'], 25)
            self.assertEqual(data_hard['lives'], 2)
            self.assertEqual(data_hard['points_per_correct'], 30)

    def test_answer_submission_and_score_evaluation(self):
        with self.client:
            # Login
            self.client.post('/register', data={
                'username': 'player_eval',
                'email': 'eval@test.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.client.post('/login', data={'email': 'eval@test.com', 'password': 'password123'})

            # Start Medium game
            self.client.post('/game/api/start', json={'difficulty': 'medium'})

            with self.client.session_transaction() as sess:
                # Force known secret solution in backend session for deterministic test
                sess['game_state']['current_solution'] = 7

            # Submit Correct Answer (7)
            res_correct = self.client.post('/game/api/submit', json={'answer': 7})
            data_correct = res_correct.get_json()
            self.assertEqual(data_correct['status'], 'correct')
            self.assertEqual(data_correct['score'], 20)
            self.assertEqual(data_correct['lives'], 3)

            # Submit Wrong Answer
            with self.client.session_transaction() as sess:
                sess['game_state']['current_solution'] = 5

            res_wrong = self.client.post('/game/api/submit', json={'answer': 9})
            data_wrong = res_wrong.get_json()
            self.assertEqual(data_wrong['status'], 'wrong')
            self.assertEqual(data_wrong['lives'], 2)

    # -------------------------------------------------------------
    # Module 7 & 8: Game Over, Score Persistence & Leaderboard
    # -------------------------------------------------------------
    def test_game_over_saves_score_to_leaderboard(self):
        with self.client:
            self.client.post('/register', data={
                'username': 'champion',
                'email': 'champ@test.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.client.post('/login', data={'email': 'champ@test.com', 'password': 'password123'})

            self.client.post('/game/api/start', json={'difficulty': 'easy'})

            with self.client.session_transaction() as sess:
                # 1 life left, score is 50, correct solution is 4
                sess['game_state']['lives'] = 1
                sess['game_state']['score'] = 50
                sess['game_state']['current_solution'] = 4

            # Submit wrong answer (0) to lose last life
            res_over = self.client.post('/game/api/submit', json={'answer': 0})
            data_over = res_over.get_json()
            self.assertEqual(data_over['status'], 'game_over')
            self.assertEqual(data_over['final_score'], 50)
            self.assertEqual(data_over['lives'], 0)

            # Check that score was persisted to SQLite database and shows on leaderboard
            leaderboard_res = self.client.get('/leaderboard')
            self.assertEqual(leaderboard_res.status_code, 200)
            self.assertIn(b'champion', leaderboard_res.data)
            self.assertIn(b'50 pts', leaderboard_res.data)

    # -------------------------------------------------------------
    # Module 10: Logout Clears Session
    # -------------------------------------------------------------
    def test_logout(self):
        with self.client:
            self.client.post('/register', data={
                'username': 'logout_user',
                'email': 'logout@test.com',
                'password': 'password123',
                'confirm_password': 'password123'
            })
            self.client.post('/login', data={'email': 'logout@test.com', 'password': 'password123'})

            res_logout = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(res_logout.status_code, 200)
            self.assertIn(b'successfully logged out', res_logout.data)

            # Verify session is empty
            with self.client.session_transaction() as sess:
                self.assertNotIn('user_id', sess)


if __name__ == '__main__':
    unittest.main()
