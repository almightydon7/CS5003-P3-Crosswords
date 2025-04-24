import sqlite3
import json
import os
import time
import hashlib

# Hash the password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Ensure the database directory exists
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Connect to the database
conn = sqlite3.connect('database/crossword.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puzzles_created INTEGER DEFAULT 0,
    puzzles_solved INTEGER DEFAULT 0
)
''')

# Create crosswords table
cursor.execute('''
CREATE TABLE IF NOT EXISTS crosswords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gridSize TEXT NOT NULL,
    visibleSquares TEXT NOT NULL,
    words TEXT NOT NULL,
    clues TEXT NOT NULL,
    lateralWords TEXT NOT NULL,
    verticalWords TEXT NOT NULL,
    creator_id INTEGER,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    difficulty_level TEXT DEFAULT 'Medium',
    times_solved INTEGER DEFAULT 0,
    average_solve_time REAL DEFAULT 0,
    validated BOOLEAN DEFAULT 1,
    FOREIGN KEY (creator_id) REFERENCES users(id)
)
''')

# Create clues table
cursor.execute('''
CREATE TABLE IF NOT EXISTS clues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crossword_id INTEGER NOT NULL,
    clue_text TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('across', 'down')),
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (crossword_id) REFERENCES crosswords(id)
)
''')

# Create crossword_words table
cursor.execute('''
CREATE TABLE IF NOT EXISTS crossword_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crossword_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('across', 'down')),
    start_x INTEGER NOT NULL,
    start_y INTEGER NOT NULL,
    end_x INTEGER NOT NULL,
    end_y INTEGER NOT NULL,
    FOREIGN KEY (crossword_id) REFERENCES crosswords(id)
)
''')

# Create crossword_visible_squares table
cursor.execute('''
CREATE TABLE IF NOT EXISTS crossword_visible_squares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crossword_id INTEGER NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    FOREIGN KEY (crossword_id) REFERENCES crosswords(id)
)
''')

# Create solutions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS solutions (
    user_id INTEGER,
    puzzle_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    solve_time REAL NOT NULL,
    attempt_count INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, puzzle_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Create leaderboards table
cursor.execute('''
CREATE TABLE IF NOT EXISTS leaderboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puzzle_id INTEGER,
    user_id INTEGER,
    solve_time REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Create puzzle_attempts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS puzzle_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    puzzle_id INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration REAL,
    successful BOOLEAN DEFAULT 0,
    progress TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Create user_best_times table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_best_times (
    user_id INTEGER,
    puzzle_id INTEGER,
    best_time REAL NOT NULL,
    timestamp DATETIME,
    PRIMARY KEY (user_id, puzzle_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Create puzzle_ratings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS puzzle_ratings (
    user_id INTEGER,
    puzzle_id INTEGER,
    rating INTEGER NOT NULL,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, puzzle_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Insert test users
cursor.execute('''
INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
''', ("admin", hash_password("admin123")))

cursor.execute('''
INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
''', ("test", hash_password("test")))

# Get admin user ID
cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
admin_id = cursor.fetchone()[0]

# Triggers
cursor.executescript('''
CREATE TRIGGER IF NOT EXISTS update_user_puzzles_solved
AFTER INSERT ON solutions
WHEN NEW.solve_time IS NOT NULL
BEGIN
    UPDATE users
    SET puzzles_solved = puzzles_solved + 1
    WHERE id = NEW.user_id;
END;

CREATE TRIGGER IF NOT EXISTS update_user_puzzles_created
AFTER INSERT ON crosswords
WHEN NEW.creator_id IS NOT NULL
BEGIN
    UPDATE users
    SET puzzles_created = puzzles_created + 1
    WHERE id = NEW.creator_id;
END;

CREATE TRIGGER IF NOT EXISTS update_crossword_times_solved
AFTER INSERT ON solutions
WHEN NEW.solve_time IS NOT NULL
BEGIN
    UPDATE crosswords
    SET times_solved = times_solved + 1
    WHERE id = NEW.puzzle_id;
END;
''')

# Commit and close
conn.commit()
conn.close()

print("Database initialized!")

