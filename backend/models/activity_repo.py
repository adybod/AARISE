from ..db import get_db


def list_activities(user_id):
    with get_db() as db:
        rows = db.execute(
            "SELECT id, content, created_at FROM activities WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def add_activity(user_id, content):
    with get_db() as db:
        db.execute("INSERT INTO activities (user_id, content) VALUES (?, ?)", (user_id, content))
