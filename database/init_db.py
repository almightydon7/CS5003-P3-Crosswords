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

# Create historical_rankings table to track user rankings over time
cursor.execute('''
CREATE TABLE IF NOT EXISTS historical_rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    puzzle_id INTEGER,
    score REAL NOT NULL,
    rank INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Create puzzle_records table for tracking puzzle solves
cursor.execute('''
CREATE TABLE IF NOT EXISTS puzzle_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    puzzle_id INTEGER,
    time_taken REAL,
    solved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
)
''')

# Create friends table for managing friend relationships
cursor.execute('''
CREATE TABLE IF NOT EXISTS friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    friend_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(username),
    FOREIGN KEY (friend_id) REFERENCES users(username)
)
''')

# Create messages table for user messaging
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(username),
    FOREIGN KEY (receiver_id) REFERENCES users(username)
)
''')

# Create puzzles table that matches the server.py code
cursor.execute('''
CREATE TABLE IF NOT EXISTS puzzles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    grid TEXT NOT NULL,
    answer TEXT NOT NULL,
    clues TEXT NOT NULL,
    times_solved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Add preset crosswords
sample_crosswords = [
    {
        "name": "Computer Science Basics",
        "gridSize": json.dumps([5, 5]),
        "visibleSquares": json.dumps([[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], 
                                      [1, 0], [1, 2], [1, 4],
                                      [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                                      [3, 0], [3, 2], [3, 4],
                                      [4, 0], [4, 1], [4, 2], [4, 3], [4, 4]]),
        "words": json.dumps(["LOGIC", "ARRAY", "CACHE", "CLASS", "DEBUG"]),
        "clues": json.dumps([
            {"id": 1, "text": "Foundation of computer science and programming", "direction": "across", "position": [0, 0], "answer": "LOGIC"},
            {"id": 2, "text": "A data structure that stores elements of the same type", "direction": "down", "position": [0, 0], "answer": "ARRAY"},
            {"id": 3, "text": "Memory used to speed up data access", "direction": "across", "position": [2, 0], "answer": "CACHE"},
            {"id": 4, "text": "A blueprint for creating objects in OOP", "direction": "down", "position": [0, 2], "answer": "CLASS"},
            {"id": 5, "text": "Find and fix errors in code", "direction": "across", "position": [4, 0], "answer": "DEBUG"}
        ]),
        "lateralWords": json.dumps({
            "LOGIC": {"start": [0, 0], "end": [0, 4]},
            "CACHE": {"start": [2, 0], "end": [2, 4]},
            "DEBUG": {"start": [4, 0], "end": [4, 4]}
        }),
        "verticalWords": json.dumps({
            "ARRAY": {"start": [0, 0], "end": [4, 0]},
            "CLASS": {"start": [0, 2], "end": [4, 2]}
        }),
        "difficulty_level": "Medium",
        "average_solve_time": 180.0  # 3 minutes average
    },
    {
        "name": "Artificial Intelligence",
        "gridSize": json.dumps([4, 4]),
        "visibleSquares": json.dumps([[0, 0], [0, 1], [0, 3], 
                                      [1, 0], [1, 1], [1, 2], [1, 3],
                                      [2, 0], [2, 1], [2, 3],
                                      [3, 0], [3, 1], [3, 2], [3, 3]]),
        "words": json.dumps(["CNN", "GPT", "NLP", "DNN"]),
        "clues": json.dumps([
            {"id": 1, "text": "Neural network type used for image processing", "direction": "across", "position": [0, 0], "answer": "CNN"},
            {"id": 2, "text": "Popular generative AI model family", "direction": "down", "position": [0, 0], "answer": "GPT"},
            {"id": 3, "text": "Machine processing of human languages", "direction": "across", "position": [1, 1], "answer": "NLP"},
            {"id": 4, "text": "Deep Neural Network", "direction": "down", "position": [1, 3], "answer": "DNN"}
        ]),
        "lateralWords": json.dumps({
            "CNN": {"start": [0, 0], "end": [0, 2]},
            "NLP": {"start": [1, 1], "end": [1, 3]}
        }),
        "verticalWords": json.dumps({
            "GPT": {"start": [0, 0], "end": [2, 0]},
            "DNN": {"start": [1, 3], "end": [3, 3]}
        }),
        "difficulty_level": "Easy",
        "average_solve_time": 120.0  # 2 minutes average
    },
    {
        "name": "St Andrews, Scotland",
        "gridSize": json.dumps([6, 6]),
        "visibleSquares": json.dumps([[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5],
                                      [1, 0], [1, 3],
                                      [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5],
                                      [3, 0], [3, 3], [3, 5],
                                      [4, 0], [4, 3], [4, 5],
                                      [5, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5]]),
        "words": json.dumps(["CASTLE", "GOLFED", "PIER", "SEA", "OLD"]),
        "clues": json.dumps([
            {"id": 1, "text": "St Andrews has ruins of a medieval one", "direction": "across", "position": [0, 0], "answer": "CASTLE"},
            {"id": 2, "text": "What many have done on the Old Course", "direction": "down", "position": [0, 3], "answer": "GOLFED"},
            {"id": 3, "text": "Harbor structure in St Andrews", "direction": "across", "position": [2, 2], "answer": "PIER"},
            {"id": 4, "text": "North ___, body of water beside St Andrews", "direction": "down", "position": [2, 5], "answer": "SEA"},
            {"id": 5, "text": "The famous '___ Course' in St Andrews", "direction": "across", "position": [5, 3], "answer": "OLD"}
        ]),
        "lateralWords": json.dumps({
            "CASTLE": {"start": [0, 0], "end": [0, 5]},
            "PIER": {"start": [2, 2], "end": [2, 5]},
            "OLD": {"start": [5, 3], "end": [5, 5]}
        }),
        "verticalWords": json.dumps({
            "GOLFED": {"start": [0, 3], "end": [5, 3]},
            "SEA": {"start": [3, 5], "end": [5, 5]}
        }),
        "difficulty_level": "Hard",
        "average_solve_time": 300.0  # 5 minutes average
    }
]

# Check if there is any crossword data
cursor.execute("SELECT COUNT(*) FROM crosswords")
count = cursor.fetchone()[0]

# Only add sample crosswords if there are none
if count == 0:
    # Add a test user first (for foreign key constraints)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', ("admin", "admin123"))
    
    # Get the admin user ID
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    admin_id = cursor.fetchone()[0]

    for crossword in sample_crosswords:
        # Insert the crossword
        cursor.execute('''
        INSERT INTO crosswords (
            name, 
            gridSize, 
            visibleSquares, 
            words, 
            clues, 
            lateralWords, 
            verticalWords,
            creator_id,
            difficulty_level,
            average_solve_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            crossword["name"],
            crossword["gridSize"],
            crossword["visibleSquares"],
            crossword["words"],
            crossword["clues"],
            crossword["lateralWords"],
            crossword["verticalWords"],
            admin_id,
            crossword["difficulty_level"],
            crossword["average_solve_time"]
        ))
        
        # Get the inserted crossword ID
        crossword_id = cursor.lastrowid
        
        # Add some fake leaderboard data
        for i in range(1, 6):  # Add 5 fake records
            fake_user = f"user{i}"
            
            # Insert fake user if not exists
            cursor.execute('''
            INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
            ''', (fake_user, "password"))
            
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (fake_user,))
            user_id = cursor.fetchone()[0]
            
            # Add to leaderboard with varying times
            solve_time = crossword["average_solve_time"] * (0.8 + (i * 0.1))  # Vary times around average
            
            cursor.execute('''
            INSERT INTO leaderboards (puzzle_id, user_id, solve_time)
            VALUES (?, ?, ?)
            ''', (crossword_id, user_id, solve_time))
            
            # Update user's personal best time
            cursor.execute('''
            INSERT INTO user_best_times (user_id, puzzle_id, best_time, timestamp)
            VALUES (?, ?, ?, datetime('now'))
            ''', (user_id, crossword_id, solve_time))
            
            # Add to solutions table
            cursor.execute('''
            INSERT OR IGNORE INTO solutions (user_id, puzzle_id, solve_time)
            VALUES (?, ?, ?)
            ''', (user_id, crossword_id, solve_time))
            
            # Add some puzzle ratings
            rating = 5 - (i % 3)  # Ratings between 3-5
            cursor.execute('''
            INSERT INTO puzzle_ratings (user_id, puzzle_id, rating, comment)
            VALUES (?, ?, ?, ?)
            ''', (user_id, crossword_id, rating, f"Great puzzle! Solved in {solve_time:.1f} seconds."))
            
            # Update user's solved puzzles count
            cursor.execute('''
            UPDATE users SET puzzles_solved = puzzles_solved + 1 WHERE id = ?
            ''', (user_id,))
            
        # Update the creator's created puzzles count
        cursor.execute('''
        UPDATE users SET puzzles_created = puzzles_created + 1 WHERE id = ?
        ''', (admin_id,))
        
        # Update crossword times_solved count
        cursor.execute('''
        UPDATE crosswords SET times_solved = ? WHERE id = ?
        ''', (5, crossword_id))
main

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
