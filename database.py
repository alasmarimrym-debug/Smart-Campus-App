import sqlite3

DB_NAME = "student_app.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            course_name TEXT NOT NULL,
            time TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_schedule(day, course_name, time):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO schedules (day, course_name, time) VALUES (?, ?, ?)",
        (day, course_name, time),
    )
    conn.commit()
    conn.close()


def get_all_schedules():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, day, course_name, time FROM schedules ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def add_task(title, status):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (title, status) VALUES (?, ?)",
        (title, status),
    )
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, title, status FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def add_flashcard(subject, question, answer):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO flashcards (subject, question, answer) VALUES (?, ?, ?)",
        (subject, question, answer),
    )
    conn.commit()
    conn.close()


def get_all_flashcards():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, subject, question, answer FROM flashcards ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows
