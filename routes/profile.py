"""
routes/profile.py - User Profile & History Blueprint
===================================================
Demonstrates:
  - Module 9: User Profile
  - Theme D: Virtual Identity
  - Displays user account info, total stats, and full score history
"""

from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.user import UserModel
from models.score import ScoreModel

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def index():
    """
    Renders the authenticated user's profile view with their registration details,
    aggregated statistics, and full chronological game history.
    """
    user_id = session['user_id']
    user = UserModel.get_by_id(user_id)
    stats = UserModel.get_user_stats(user_id)
    history = ScoreModel.get_user_history(user_id, limit=25)

    return render_template(
        'profile.html',
        user=user,
        stats=stats,
        history=history
    )
