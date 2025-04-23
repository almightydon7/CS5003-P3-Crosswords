# database.py
import sqlite3
import json

DB_NAME = "crossword_game.db"

def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            puzzles_solved INTEGER DEFAULT 0,
            puzzles_created INTEGER DEFAULT 0
        )
    """)
    
    # Create puzzles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            grid TEXT NOT NULL,
            answer TEXT NOT NULL,
            clues TEXT NOT NULL,
            times_solved INTEGER DEFAULT 0,
            average_time REAL DEFAULT 0,
            FOREIGN KEY (author) REFERENCES users (username)
        )
    """)
    
    # Create puzzle_records table to track time taken per solve
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puzzle_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            puzzle_id INTEGER NOT NULL,
            time_taken INTEGER NOT NULL,
            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username),
            FOREIGN KEY (puzzle_id) REFERENCES puzzles (id)
        )
    """)

    # Add sample puzzles if none exist
    cursor.execute("SELECT COUNT(*) FROM puzzles")
    if cursor.fetchone()[0] == 0:
        sample_puzzles = [
            {
                'title': 'Simple Crossword 1',
                'author': 'system',
                'grid': json.dumps([
                    ['T', '_', 'P'],
                    ['_', 'R', '_'],
                    ['P', '_', 'N']
                ]),
                'answer': json.dumps([
                    ['T', 'O', 'P'],
                    ['A', 'R', 'E'],
                    ['P', 'E', 'N']
                ]),
                'clues': json.dumps({
                    'across': [
                        '1. The highest point or part.',
                        '2. Used with you, we, or they',
                        '3. A writing instrument'
                    ],
                    'down': [
                        '1. To lightly touch',
                        '2. Natural rock with metal',
                        '3. A writing instrument'
                    ]
                })
            },
            {
                'title': 'Simple Crossword 2',
                'author': 'system',
                'grid': json.dumps([
                    ['F', '_', 'N'],
                    ['_', 'R', '_'],
                    ['N', '_', 'T']
                ]),
                'answer': json.dumps([
                    ['F', 'A', 'N'],
                    ['A', 'R', 'E'],
                    ['N', 'E', 'T']
                ]),
                'clues': json.dumps({
                    'across': [
                        '1. Someone who supports a person/team',
                        '2. Present tense of “to be',
                        '3. A mesh used for catching fish'
                    ],
                    'down': [
                        '1. Someone who supports a person/team',
                        '2. Present tense of “to be',
                        '3. A mesh used for catching fish'
                    ]
                })
            }
        ]
        
        for puzzle in sample_puzzles:
            cursor.execute("""
            INSERT INTO puzzles (title, author, grid, answer, clues)
            VALUES (?, ?, ?, ?, ?)
            """, (
                puzzle['title'],
                puzzle['author'],
                puzzle['grid'],
                puzzle['answer'],
                puzzle['clues']
            ))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)

if __name__ == "__main__":
    init_db()