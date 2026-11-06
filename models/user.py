"""
models/user.py - User Data Model & Identity Helper
==================================================
Demonstrates:
  - Theme D: Virtual Identity
    * Password hashing using Werkzeug (never storing plaintext passwords)
    * Unique identity constraints (username and email)
    * Session authentication verification
"""

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import sqlite3


class UserModel:
    """Handles all user database operations using parameterized queries."""

    @staticmethod
    def create_user(username, email, password):
        """
        Creates a new user record with securely hashed password.
        Uses Werkzeug's generate_password_hash (scrypt/pbkdf2).
        Returns:
            (user_id, None) on success
            (None, error_message) on failure
        """
        db = get_db()
        # Hash password securely with salt
        password_hash = generate_password_hash(password)

        try:
            cursor = db.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username.strip(), email.strip().lower(), password_hash)
            )
            db.commit()
            return cursor.lastrowid, None
        except sqlite3.IntegrityError as e:
            err = str(e).lower()
            if "email" in err:
                return None, "An account with this email address already exists."
            elif "username" in err:
                return None, "This username is already taken. Please choose another."
            return None, "Registration failed due to a database constraint."
        except Exception as e:
            return None, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def get_by_email(email):
        """Retrieves user row by email (case-insensitive)."""
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
            (email.strip(),)
        ).fetchone()

    @staticmethod
    def get_by_username(username):
        """Retrieves user row by username (case-insensitive)."""
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username.strip(),)
        ).fetchone()

    @staticmethod
    def get_by_id(user_id):
        """Retrieves user row by primary key id."""
        db = get_db()
        return db.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    @staticmethod
    def verify_password(stored_hash, password):
        """Verifies plaintext password against the stored cryptographic hash."""
        return check_password_hash(stored_hash, password)

    @staticmethod
    def get_user_stats(user_id):
        """
        Aggregates gaming performance metrics for the authenticated user.
        Calculates:
          - Total games played
          - Highest single-game score
          - Cumulative score
          - Average score
        """
        db = get_db()
        row = db.execute(
            """
            SELECT 
                COUNT(*) AS total_games,
                COALESCE(MAX(score), 0) AS highest_score,
                COALESCE(SUM(score), 0) AS total_score,
                COALESCE(ROUND(AVG(score), 1), 0.0) AS average_score
            FROM scores
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        return {
            "total_games": row["total_games"],
            "highest_score": row["highest_score"],
            "total_score": row["total_score"],
            "average_score": row["average_score"]
        }
