"""
models/score.py - Score Management Model
========================================
Demonstrates:
  - Theme D: Virtual Identity (associating game performance directly with user accounts)
  - Parameterized database operations
  - Aggregated leaderboard queries
"""

from database import get_db


class ScoreModel:
    """Handles all score storage and leaderboard data retrieval."""

    @staticmethod
    def save_score(user_id, score, difficulty):
        """
        Saves a finalized game score into the database.
        Ensures foreign key association to the active player's user account.
        """
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO scores (user_id, score, difficulty)
            VALUES (?, ?, ?)
            """,
            (user_id, int(score), str(difficulty).capitalize())
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_leaderboard(limit=10):
        """
        Retrieves the top players based on their single highest score.
        Uses SQL aggregation with GROUP BY user_id and ORDER BY highest_score DESC.
        Returns a list of dicts with rank, username, high_score, total_games, and last_played.
        """
        db = get_db()
        rows = db.execute(
            """
            SELECT 
                u.id AS user_id,
                u.username,
                MAX(s.score) AS highest_score,
                COUNT(s.id) AS games_played,
                MAX(s.created_at) AS last_played
            FROM scores s
            JOIN users u ON s.user_id = u.id
            GROUP BY u.id, u.username
            ORDER BY highest_score DESC, games_played DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        leaderboard = []
        for index, row in enumerate(rows, start=1):
            leaderboard.append({
                "rank": index,
                "username": row["username"],
                "highest_score": row["highest_score"],
                "games_played": row["games_played"],
                "last_played": row["last_played"]
            })
        return leaderboard

    @staticmethod
    def get_user_history(user_id, limit=15):
        """Retrieves recent game logs for a specific user."""
        db = get_db()
        return db.execute(
            """
            SELECT id, score, difficulty, created_at
            FROM scores
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
