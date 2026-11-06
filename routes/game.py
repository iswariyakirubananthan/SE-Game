"""
routes/game.py - Game Logic, Difficulty Rules & Gameplay Blueprint
==================================================================
Demonstrates:
  - Module 5: Difficulty Selection (Easy, Medium, Hard)
  - Module 6: Main Gameplay & Banana Game API integration
  - Module 7: Server-side Score Calculation & Persistence
  - Theme B: Interoperability (REST API communication)
  - Theme C: Event-Driven responses for answer submission & timer expiration
  - Theme D: Virtual Identity (Associating scores with authenticated user)
  - CRITICAL SECURITY: Correct puzzle solutions are NEVER exposed to client-side JS or HTML.
"""

from flask import Blueprint, render_template, request, jsonify, session, g, redirect, url_for, flash
from routes.auth import login_required
from services.banana_service import BananaApiService
from models.score import ScoreModel
import copy

game_bp = Blueprint('game', __name__, url_prefix='/game')

# Difficulty Configurations (Backend-Enforced)
DIFFICULTY_CONFIGS = {
    'easy': {
        'name': 'Easy',
        'time_limit': 60,      # 60 seconds per question
        'lives': 3,            # 3 lives
        'points': 10,          # 10 points per correct answer
        'badge': 'bg-emerald-500'
    },
    'medium': {
        'name': 'Medium',
        'time_limit': 40,      # 40 seconds per question
        'lives': 3,            # 3 lives
        'points': 20,          # 20 points per correct answer
        'badge': 'bg-amber-500'
    },
    'hard': {
        'name': 'Hard',
        'time_limit': 25,      # 25 seconds per question
        'lives': 2,            # 2 lives
        'points': 30,          # 30 points per correct answer
        'badge': 'bg-rose-500'
    }
}


@game_bp.route('/difficulty')
@login_required
def difficulty():
    """
    Module 5: Difficulty Selection View
    Allows authenticated users to select from Easy, Medium, or Hard modes.
    """
    return render_template('difficulty.html', configs=DIFFICULTY_CONFIGS)


@game_bp.route('/play')
@login_required
def play():
    """
    Module 6: Main Game Arena View
    Renders the game interface. Difficulty defaults to 'medium' if unspecified.
    """
    selected_difficulty = request.args.get('difficulty', 'medium').lower()
    if selected_difficulty not in DIFFICULTY_CONFIGS:
        selected_difficulty = 'medium'

    config = DIFFICULTY_CONFIGS[selected_difficulty]
    return render_template(
        'game.html',
        difficulty=selected_difficulty,
        config=config
    )


@game_bp.route('/api/start', methods=['POST'])
@login_required
def api_start_game():
    """
    Initializes a new game session on the server.
    Fetches the first puzzle from the Banana API and stores the solution
    strictly in the server-side Flask session.
    """
    data = request.get_json() or {}
    difficulty_key = data.get('difficulty', 'medium').lower()

    if difficulty_key not in DIFFICULTY_CONFIGS:
        difficulty_key = 'medium'

    config = DIFFICULTY_CONFIGS[difficulty_key]

    # Interoperability: Fetch initial puzzle from Banana API
    puzzle = BananaApiService.fetch_puzzle()

    # Create server-side game state inside Flask's encrypted session
    game_state = {
        'active': True,
        'difficulty': difficulty_key,
        'time_limit': config['time_limit'],
        'lives': config['lives'],
        'points_per_correct': config['points'],
        'score': 0,
        'questions_attempted': 1,
        'current_solution': puzzle['solution'],  # SECURE: Kept on backend only!
        'current_question_url': puzzle['question'],
        'score_saved': False
    }

    session['game_state'] = game_state
    session.modified = True

    # Return game configuration to client WITHOUT the solution
    return jsonify({
        'status': 'success',
        'question_image': puzzle['question'],
        'difficulty': difficulty_key,
        'time_limit': config['time_limit'],
        'lives': config['lives'],
        'score': 0,
        'question_number': 1,
        'points_per_correct': config['points']
    })


@game_bp.route('/api/submit', methods=['POST'])
@login_required
def api_submit_answer():
    """
    Evaluates player's answer on the backend.
    Enforces scoring, life deduction, game-over trigger, and automatic puzzle loading.
    """
    game_state = session.get('game_state')

    if not game_state or not game_state.get('active'):
        return jsonify({
            'status': 'error',
            'message': 'No active game in progress. Please start a new game.'
        }), 400

    data = request.get_json() or {}
    player_input = data.get('answer')

    # Input Validation
    if player_input is None or str(player_input).strip() == '':
        return jsonify({
            'status': 'error',
            'message': 'Please provide a numerical answer.'
        }), 400

    try:
        player_answer = int(str(player_input).strip())
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Answer must be an integer number.'
        }), 400

    # Backend verification against stored secret solution
    correct_solution = game_state['current_solution']
    is_correct = (player_answer == correct_solution)

    if is_correct:
        # Award points based on difficulty rules
        pts = game_state['points_per_correct']
        game_state['score'] += pts
        game_state['questions_attempted'] += 1

        # Interoperability: Fetch next puzzle for seamless continuation
        next_puzzle = BananaApiService.fetch_puzzle()
        game_state['current_solution'] = next_puzzle['solution']
        game_state['current_question_url'] = next_puzzle['question']

        session['game_state'] = game_state
        session.modified = True

        return jsonify({
            'status': 'correct',
            'message': f'Well done! Correct answer (+{pts} points)',
            'score': game_state['score'],
            'lives': game_state['lives'],
            'question_number': game_state['questions_attempted'],
            'next_question_image': next_puzzle['question']
        })

    else:
        # Incorrect answer: Deduct 1 life
        game_state['lives'] -= 1

        if game_state['lives'] <= 0:
            # Game Over!
            game_state['active'] = False
            final_score = game_state['score']

            # Persist score if not already saved
            if not game_state.get('score_saved'):
                ScoreModel.save_score(
                    user_id=session['user_id'],
                    score=final_score,
                    difficulty=game_state['difficulty']
                )
                game_state['score_saved'] = True

            session['game_state'] = game_state
            session.modified = True

            return jsonify({
                'status': 'game_over',
                'message': f'Incorrect! The correct answer was {correct_solution}. You have run out of lives!',
                'correct_solution': correct_solution,
                'final_score': final_score,
                'lives': 0
            })

        else:
            # Lives remain: Advance to next puzzle
            game_state['questions_attempted'] += 1
            next_puzzle = BananaApiService.fetch_puzzle()
            game_state['current_solution'] = next_puzzle['solution']
            game_state['current_question_url'] = next_puzzle['question']

            session['game_state'] = game_state
            session.modified = True

            return jsonify({
                'status': 'wrong',
                'message': f'Incorrect! The correct answer was {correct_solution}. You lost 1 life.',
                'correct_solution': correct_solution,
                'score': game_state['score'],
                'lives': game_state['lives'],
                'question_number': game_state['questions_attempted'],
                'next_question_image': next_puzzle['question']
            })


@game_bp.route('/api/timeout', methods=['POST'])
@login_required
def api_timeout():
    """
    Event handler for countdown timer expiration.
    Deducts 1 life and loads the next puzzle or terminates the game.
    """
    game_state = session.get('game_state')

    if not game_state or not game_state.get('active'):
        return jsonify({'status': 'error', 'message': 'No active game.'}), 400

    correct_solution = game_state['current_solution']
    game_state['lives'] -= 1

    if game_state['lives'] <= 0:
        # Time ran out on final life: Game Over
        game_state['active'] = False
        final_score = game_state['score']

        if not game_state.get('score_saved'):
            ScoreModel.save_score(
                user_id=session['user_id'],
                score=final_score,
                difficulty=game_state['difficulty']
            )
            game_state['score_saved'] = True

        session['game_state'] = game_state
        session.modified = True

        return jsonify({
            'status': 'game_over',
            'message': f"Time is up! The correct answer was {correct_solution}. Game over!",
            'correct_solution': correct_solution,
            'final_score': final_score,
            'lives': 0
        })
    else:
        # Continue with next puzzle
        game_state['questions_attempted'] += 1
        next_puzzle = BananaApiService.fetch_puzzle()
        game_state['current_solution'] = next_puzzle['solution']
        game_state['current_question_url'] = next_puzzle['question']

        session['game_state'] = game_state
        session.modified = True

        return jsonify({
            'status': 'timeout',
            'message': f"Time expired! The answer was {correct_solution}. You lost 1 life.",
            'correct_solution': correct_solution,
            'score': game_state['score'],
            'lives': game_state['lives'],
            'question_number': game_state['questions_attempted'],
            'next_question_image': next_puzzle['question']
        })


@game_bp.route('/api/quit', methods=['POST'])
@login_required
def api_quit_game():
    """
    Allows a player to end their game early, persisting their current score.
    """
    game_state = session.get('game_state')
    if game_state and game_state.get('active'):
        game_state['active'] = False
        if not game_state.get('score_saved') and game_state['score'] > 0:
            ScoreModel.save_score(
                user_id=session['user_id'],
                score=game_state['score'],
                difficulty=game_state['difficulty']
            )
            game_state['score_saved'] = True
        session['game_state'] = game_state
        session.modified = True

    return jsonify({'status': 'quit_success', 'redirect': url_for('dashboard.index')})
