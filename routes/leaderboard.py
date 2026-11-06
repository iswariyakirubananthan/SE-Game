"""
routes/leaderboard.py - Leaderboard Blueprint
=============================================
Demonstrates:
  - Module 8: Leaderboard
  - Top 10 rankings retrieved dynamically from SQLite
  - Updates automatically as new game scores are submitted
"""

from flask import Blueprint, render_template, session
from models.score import ScoreModel
from routes.auth import login_required

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/leaderboard')
def index():
    """
    Renders the public or authenticated leaderboard ranking the top 10 players.
    Highlights the logged-in user if they appear on the board.
    """
    top_players = ScoreModel.get_leaderboard(limit=10)
    current_username = session.get('username')

    return render_template(
        'leaderboard.html',
        leaderboard=top_players,
        current_username=current_username
    )
