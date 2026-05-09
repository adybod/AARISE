from ..db import get_db


def get_profile(user_id):
    with get_db() as db:
        row = db.execute(
            "SELECT grade, targets, goal FROM profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else {"grade": "", "targets": "", "goal": ""}


def update_profile(user_id, grade, targets, goal):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO profiles (user_id, grade, targets, goal, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                grade = excluded.grade,
                targets = excluded.targets,
                goal = excluded.goal,
                updated_at = datetime('now')
            """,
            (user_id, grade, targets, goal),
        )
