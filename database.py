import sqlite3
from datetime import date, datetime
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "database" / "assignments.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
                deadline TEXT NOT NULL,
                estimated_hours REAL NOT NULL CHECK (estimated_hours > 0),
                status TEXT NOT NULL CHECK (status IN ('Pending', 'In Progress', 'Completed')),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                assignment_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def list_assignments():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM assignments ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_assignment(assignment_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM assignments WHERE id = ?", (assignment_id,)
        ).fetchone()
    return dict(row) if row else None


def save_assignment(values, assignment_id=None):
    with get_connection() as connection:
        if assignment_id is None:
            cursor = connection.execute(
                """INSERT INTO assignments
                   (name, subject, description, difficulty, deadline, estimated_hours, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (*values, datetime.now().isoformat(timespec="seconds")),
            )
            return cursor.lastrowid
        connection.execute(
            """UPDATE assignments
               SET name = ?, subject = ?, description = ?, difficulty = ?, deadline = ?,
                   estimated_hours = ?, status = ?
               WHERE id = ?""",
            (*values, assignment_id),
        )
    return assignment_id


def delete_assignment(assignment_id):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    return cursor.rowcount > 0


def log_activity(action, assignment_name):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO activity (action, assignment_name, created_at) VALUES (?, ?, ?)",
            (action, assignment_name, datetime.now().isoformat(timespec="seconds")),
        )


def recent_activity(limit=8):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM activity ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def assignment_counts():
    today = date.today().isoformat()
    with get_connection() as connection:
        row = connection.execute(
            """SELECT COUNT(*) AS total,
                      SUM(status = 'Pending') AS pending,
                      SUM(status = 'In Progress') AS in_progress,
                      SUM(status = 'Completed') AS completed,
                      SUM(status != 'Completed' AND deadline < ?) AS overdue,
                      SUM(status != 'Completed' AND deadline >= ? AND deadline <= date(?, '+3 days')) AS due_soon
               FROM assignments""",
            (today, today, today),
        ).fetchone()
    return {key: row[key] or 0 for key in row.keys()}


initialize_database()