"""
routes/dashboard.py - User Dashboard Blueprint
=============================================
Demonstrates:
  - Module 4: Game Dashboard
  - Aggregating and displaying user's real-time statistics (total score, games, high score)
  - Protected route requiring active session identity
"""

from flask import Blueprint, render_template, session, g
from routes.auth import login_required
from models.user import UserModel
from models.score import ScoreModel

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Displays the user dashboard with their username, personal high score,
    games played, total score, and recent activity.
    """
    user_id = session['user_id']
    stats = UserModel.get_user_stats(user_id)
    recent_scores = ScoreModel.get_user_history(user_id, limit=5)

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_scores=recent_scores
    )
