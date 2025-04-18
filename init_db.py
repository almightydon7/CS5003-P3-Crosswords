import sqlite3
import os

def setup_database():
    # Ensure the database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect('database/crossword.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crosswords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gridSize TEXT NOT NULL,
        visibleSquares TEXT NOT NULL,
        words TEXT NOT NULL,
        clues TEXT NOT NULL,
        lateralWords TEXT NOT NULL,
        verticalWords TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS solutions (
        user_id INTEGER,
        puzzle_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, puzzle_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (puzzle_id) REFERENCES crosswords(id)
    )
    ''')
    
    conn.commit()
    return conn

if __name__ == "__main__":
    conn = setup_database()
    conn.close()
    print("Database structure created!✔️")
