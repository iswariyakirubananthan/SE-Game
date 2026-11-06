"""
routes/auth.py - Authentication & Session Identity Blueprint
============================================================
Demonstrates:
  - Theme D: Virtual Identity
    * Secure Registration with Werkzeug password hashing
    * Authentication via Email & Password validation
    * Flask session-based identity state & cookie management
    * Protected route decorator (@login_required)
    * Session termination (Logout)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from functools import wraps
import re
from models.user import UserModel

auth_bp = Blueprint('auth', __name__)


def login_required(view):
    """
    Decorator that enforces authentication on protected routes.
    If the user is not authenticated in the session, they are redirected
    to the login page with an informative message.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this area.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return view(**kwargs)
    return wrapped_view


@auth_bp.before_app_request
def load_logged_in_user():
    """
    Flask hook that runs before every incoming request.
    If a user_id exists in session cookies, loads the user record into Flask's 'g' context.
    This makes user information readily available in all Jinja templates.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = UserModel.get_by_id(user_id)


def is_valid_email(email):
    """Validates email format using regex pattern."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email.strip()) is not None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Module 2: User Registration
    Validates input fields, verifies email uniqueness, hashes password, and persists user.
    """
    # If already logged in, redirect to dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side Validation
        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template('register.html', username=username, email=email)

        if len(username) < 3 or len(username) > 25:
            flash("Username must be between 3 and 25 characters.", "danger")
            return render_template('register.html', username=username, email=email)

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash("Username can only contain letters, numbers, and underscores.", "danger")
            return render_template('register.html', username=username, email=email)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', username=username, email=email)

        # Attempt User Creation
        user_id, error = UserModel.create_user(username, email, password)
        if error:
            flash(error, "danger")
            return render_template('register.html', username=username, email=email)

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Module 3: User Login
    Verifies credentials and initializes the authenticated session identity.
    """
    # If already logged in, redirect to dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template('login.html', email=email)

        user = UserModel.get_by_email(email)

        # Constant-time comparison via Werkzeug check_password_hash prevents timing attacks
        if user is None or not UserModel.verify_password(user['password_hash'], password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html', email=email)

        # Establish Virtual Identity in Flask Session
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session.permanent = True  # Uses app.config['PERMANENT_SESSION_LIFETIME']

        flash(f"Welcome back, {user['username']}! Ready to solve some banana puzzles?", "success")

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    Module 10: Logout
    Clears the authenticated Flask session and redirects to the home page.
    """
    session.clear()
    flash("You have been successfully logged out. See you next time!", "info")
    return redirect(url_for('home.index'))
