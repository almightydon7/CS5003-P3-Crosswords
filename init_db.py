import sqlite3
import json
import os

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
    password TEXT NOT NULL
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
    verticalWords TEXT NOT NULL
)
''')

# Create solutions table
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
        })
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
        })
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
        })
    }
]

# Check if there is any crossword data
cursor.execute("SELECT COUNT(*) FROM crosswords")
count = cursor.fetchone()[0]

# Only add sample crosswords if there are none
if count == 0:
    for crossword in sample_crosswords:
        cursor.execute('''
        INSERT INTO crosswords (name, gridSize, visibleSquares, words, clues, lateralWords, verticalWords)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            crossword["name"],
            crossword["gridSize"],
            crossword["visibleSquares"],
            crossword["words"],
            crossword["clues"],
            crossword["lateralWords"],
            crossword["verticalWords"]
        ))

# Commit and close the connection
conn.commit()
conn.close()

print("Database initialized!✔️") 