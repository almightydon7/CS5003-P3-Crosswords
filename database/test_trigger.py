import sqlite3

conn = sqlite3.connect('database/crossword.db')
cursor = conn.cursor()

print("=== Trigger Test Start ===")

# Step 1: Create test user and puzzle if not exists
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("trigger_tester", "test123"))
cursor.execute("SELECT id FROM users WHERE username = ?", ("trigger_tester",))
user_id = cursor.fetchone()[0]

cursor.execute("INSERT INTO crosswords (name, gridSize, visibleSquares, words, clues, lateralWords, verticalWords, creator_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
    ("Trigger Test Puzzle", "[3,3]", "[]", "[]", "[]", "{}", "{}", user_id))
puzzle_id = cursor.lastrowid

# Step 2: Check initial stats
cursor.execute("SELECT puzzles_created, puzzles_solved FROM users WHERE id = ?", (user_id,))
created_before, solved_before = cursor.fetchone()

cursor.execute("SELECT times_solved FROM crosswords WHERE id = ?", (puzzle_id,))
times_solved_before = cursor.fetchone()[0]

print(f"[Before] User puzzles_created: {created_before}, puzzles_solved: {solved_before}")
print(f"[Before] Crossword times_solved: {times_solved_before}")

# Step 3: Insert a solution to trigger both user & crossword updates
cursor.execute("INSERT INTO solutions (user_id, puzzle_id, solve_time) VALUES (?, ?, ?)", (user_id, puzzle_id, 123.4))

# Step 4: Check values after trigger
cursor.execute("SELECT puzzles_created, puzzles_solved FROM users WHERE id = ?", (user_id,))
created_after, solved_after = cursor.fetchone()

cursor.execute("SELECT times_solved FROM crosswords WHERE id = ?", (puzzle_id,))
times_solved_after = cursor.fetchone()[0]

print(f"[After]  User puzzles_created: {created_after}, puzzles_solved: {solved_after}")
print(f"[After]  Crossword times_solved: {times_solved_after}")

# Done
conn.commit()
conn.close()
print("=== Trigger Test Complete ===")
