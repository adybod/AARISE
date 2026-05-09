from ..db import get_db


def get_user_by_email(email):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def create_user(email, name, role):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO users (email, name, role, auth_provider) VALUES (?, ?, ?, 'google')",
            (email, name, role),
        )
        user_id = cur.lastrowid
        db.execute("INSERT INTO profiles (user_id, grade, targets, goal) VALUES (?, '', '', '')", (user_id,))
        return get_user_by_id(user_id)
