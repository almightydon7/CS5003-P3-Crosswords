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
                    [
                        {"char": "T", "is_black": False},
                        {"char": "", "is_black": False},
                        {"char": "P", "is_black": False}
                    ],
                    [
                        {"char": "", "is_black": False},
                        {"char": "R", "is_black": False},
                        {"char": "", "is_black": False}
                    ],
                    [
                        {"char": "P", "is_black": False},
                        {"char": "", "is_black": False},
                        {"char": "N", "is_black": False}
                    ]
                ]),
                'answer': json.dumps([
                    ["T", "O", "P"],
                    ["A", "R", "E"],
                    ["P", "E", "N"]
                ]),
                'clues': json.dumps({
                    'across': [
                        {"number": 1, "text": "The highest point or part"},
                        {"number": 2, "text": "Used with you, we, or they"},
                        {"number": 3, "text": "A writing instrument"}
                    ],
                    'down': [
                        {"number": 1, "text": "To lightly touch"},
                        {"number": 2, "text": "Natural rock with metal"},
                        {"number": 3, "text": "A writing instrument"}
                    ]
                })
            },
            {
                'title': 'Simple Crossword 2',
                'author': 'system',
                'grid': json.dumps([
                    [
                        {"char": "F", "is_black": False},
                        {"char": "", "is_black": False},
                        {"char": "N", "is_black": False}
                    ],
                    [
                        {"char": "", "is_black": False},
                        {"char": "R", "is_black": False},
                        {"char": "", "is_black": False}
                    ],
                    [
                        {"char": "N", "is_black": False},
                        {"char": "", "is_black": False},
                        {"char": "T", "is_black": False}
                    ]
                ]),
                'answer': json.dumps([
                    ["F", "A", "N"],
                    ["A", "R", "E"],
                    ["N", "E", "T"]
                ]),
                'clues': json.dumps({
                    'across': [
                        {"number": 1, "text": "A device that moves air"},
                        {"number": 2, "text": "Present tense of 'to be'"},
                        {"number": 3, "text": "A mesh used for catching fish"}
                    ],
                    'down': [
                        {"number": 1, "text": "Someone who supports a person/team"},
                        {"number": 2, "text": "A negative word"},
                        {"number": 3, "text": "Clean and tidy"}
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