"""
app.py - Main Application Factory and Server Entry Point
=======================================================
Banana Quest - Brain Challenge
University of Bedfordshire - Computer Science Assignment

Architecture: Distributed Architecture
  [Browser Frontend (HTML5/CSS3/JS)]
               |
          HTTP / JSON
               v
      [Flask Backend (Python 3)]
        /                     \
  SQLite (Database)     Banana Game API (REST Service)

Demonstrates Core Themes:
  A. Version Control (Git commits, feature branches, merging)
  B. Interoperability (HTTP client, external JSON consumption, fallback)
  C. Event-Driven Programming (DOM events, timers, async fetch)
  D. Virtual Identity (Authentication, Werkzeug hashing, session state)
"""

import os
from datetime import timedelta
from flask import Flask, render_template
import database

# Import application blueprints
from routes.home import home_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.game import game_bp
from routes.leaderboard import leaderboard_bp
from routes.profile import profile_bp


def create_app(test_config=None):
    """
    Application factory function.
    Configures settings, database hooks, and registers all module blueprints.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Core Security & Session Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'banana-quest-super-secret-key-uob-2026'),
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_COOKIE_HTTPONLY=True,       # Mitigates XSS cookie theft
        SESSION_COOKIE_SAMESITE='Lax',      # Mitigates CSRF
    )

    if test_config:
        app.config.update(test_config)

    # Initialize SQLite database layer
    database.init_app(app)

    with app.app_context():
        database.init_db()

    # Register Module Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(profile_bp)

    # Global Context Processor (makes current year and app name available in templates)
    @app.context_processor
    def inject_app_metadata():
        return {
            'app_title': 'Banana Quest – Brain Challenge',
            'current_year': 2026
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app


# Create application instance
app = create_app()

if __name__ == '__main__':
    # Run the Flask development server on localhost:5000
    print("=" * 60)
    print("  Banana Quest – Brain Challenge is starting!")
    print("  Local Server: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
