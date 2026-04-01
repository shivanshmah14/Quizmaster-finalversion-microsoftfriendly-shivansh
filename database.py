"""
Database module for QuizMaster - Phase 2
Handles SQLite database operations, user authentication, and CRUD for questions/scores
"""

import sqlite3
from pathlib import Path
import hashlib
import json

DATABASE_PATH = Path(__file__).parent / "data" / "quizmaster.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            points INTEGER DEFAULT 10,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password, is_admin=False):
    if not username or not password:
        return False, "Username and password are required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, hash_password(password), is_admin),
        )
        conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password)),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "username": row["username"],
            "is_admin": bool(row["is_admin"]),
            "created_at": row["created_at"],
        }
    return None


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_question(
    category, question, options, correct_index, difficulty="medium", points=10, created_by=None
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO questions
        (category, question, options, correct_index, difficulty, points, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (category, question, json.dumps(options), correct_index, difficulty, points, created_by),
    )
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id


def get_questions_by_category(category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE category = ? ORDER BY id", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "category": row["category"],
            "question": row["question"],
            "options": json.loads(row["options"]),
            "correct": row["correct_index"],
            "difficulty": row["difficulty"],
            "points": row["points"],
            "created_by": row["created_by"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def get_question_by_id(question_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "category": row["category"],
            "question": row["question"],
            "options": json.loads(row["options"]),
            "correct": row["correct_index"],
            "difficulty": row["difficulty"],
            "points": row["points"],
            "created_by": row["created_by"],
        }
    return None


def update_question(
    question_id, category=None, question=None, options=None, correct_index=None, difficulty=None, points=None
):
    conn = get_connection()
    cursor = conn.cursor()
    updates, values = [], []
    if category is not None:
        updates.append("category = ?")
        values.append(category)
    if question is not None:
        updates.append("question = ?")
        values.append(question)
    if options is not None:
        updates.append("options = ?")
        values.append(json.dumps(options))
    if correct_index is not None:
        updates.append("correct_index = ?")
        values.append(correct_index)
    if difficulty is not None:
        updates.append("difficulty = ?")
        values.append(difficulty)
    if points is not None:
        updates.append("points = ?")
        values.append(points)
    if not updates:
        conn.close()
        return False
    values.append(question_id)
    cursor.execute(f"UPDATE questions SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_question(question_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def save_score(user_id, category, score, correct_answers, total_questions):
    conn = get_connection()
    cursor = conn.cursor()
    percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    cursor.execute(
        """
        INSERT INTO scores
        (user_id, category, score, correct_answers, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (user_id, category, score, correct_answers, total_questions, percentage),
    )
    conn.commit()
    conn.close()


def get_highscores(limit=10, category=None):
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute(
            """
            SELECT s.*, u.username
            FROM scores s
            JOIN users u ON s.user_id = u.id
            WHERE s.category = ?
            ORDER BY s.score DESC, s.played_at DESC
            LIMIT ?
        """,
            (category, limit),
        )
    else:
        cursor.execute(
            """
            SELECT s.*, u.username
            FROM scores s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.score DESC, s.played_at DESC
            LIMIT ?
        """,
            (limit,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "username": row["username"],
            "user_id": row["user_id"],
            "category": row["category"],
            "score": row["score"],
            "correct_answers": row["correct_answers"],
            "total_questions": row["total_questions"],
            "percentage": row["percentage"],
            "played_at": row["played_at"],
        }
        for row in rows
    ]


def get_user_scores(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM scores WHERE user_id = ?
        ORDER BY played_at DESC LIMIT ?
    """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_statistics(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) as total_games,
            AVG(score) as avg_score,
            MAX(score) as best_score,
            AVG(percentage) as avg_percentage,
            SUM(correct_answers) as total_correct,
            SUM(total_questions) as total_questions
        FROM scores WHERE user_id = ?
    """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def migrate_json_to_db(questions_json_path):
    try:
        with open(questions_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for category, questions in data.get("categories", {}).items():
            for q in questions:
                add_question(
                    category=category,
                    question=q["question"],
                    options=q["options"],
                    correct_index=q["correct"],
                    difficulty=q.get("difficulty", "medium"),
                    points=q.get("points", 10),
                    created_by=None,
                )
                count += 1
        return count
    except Exception as e:
        print(f"Migration error: {e}")
        return 0


init_database()
