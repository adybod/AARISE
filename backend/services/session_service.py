import secrets

from ..config import SESSION_TTL_SECONDS
from ..db import get_db


def create_session(user_id):
    token = secrets.token_urlsafe(32)
    with get_db() as db:
        db.execute(
            """
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, datetime('now', ?))
            """,
            (token, user_id, f"+{SESSION_TTL_SECONDS} seconds"),
        )
    return token


def get_session_user_id(token):
    if not token:
        return None
    with get_db() as db:
        row = db.execute(
            """
            SELECT user_id FROM sessions
            WHERE token = ? AND expires_at > datetime('now')
            """,
            (token,),
        ).fetchone()
        return row["user_id"] if row else None


def delete_session(token):
    if not token:
        return
    with get_db() as db:
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
