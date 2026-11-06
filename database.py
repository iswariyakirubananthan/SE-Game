"""
database.py - SQLite Database Management Layer
==============================================
Demonstrates:
  - Theme D: Virtual Identity (storing credentials, user profiles, and persistent stats)
  - Security: Parameterized SQL queries (protects against SQL Injection)
  - Integrity: Foreign key enforcement with CASCADE deletion

AI / Development Attribution:
  - Developed for University of Bedfordshire Computer Science Assignment
"""

import sqlite3
import os
from flask import g, current_app

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')


def get_db():
    """
    Establishes and returns a connection to the SQLite database.
    Stores the connection in Flask's application context 'g' so each web request
    reuses the same connection, and closes it when the request completes.
    """
    if 'db' not in g:
        # Ensure the instance directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        g.db = sqlite3.connect(
            DATABASE_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row enables dict-like attribute access on query results (e.g., row['username'])
        g.db.row_factory = sqlite3.Row
        # Enforce foreign key constraints in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    """Closes the database connection at the end of a request context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Initializes the database schema if tables do not already exist.
    Creates:
      1. users: Stores digital identity, hashed credentials, and account creation dates.
      2. scores: Stores game performance records linked to users via foreign key.
    """
    db = get_db()

    # Table 1: Users table for Virtual Identity
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table 2: Scores table with Foreign Key linking to Users
    db.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # Performance indices for fast leaderboard queries and profile queries
    db.execute("CREATE INDEX IF NOT EXISTS idx_scores_user ON scores(user_id);")
    db.execute("CREATE INDEX IF NOT EXISTS idx_scores_score ON scores(score DESC);")

    db.commit()


def init_app(app):
    """Registers database teardown hooks with the Flask application instance."""
    app.teardown_appcontext(close_db)
