import sqlite3
import json
import time
import os
from datetime import datetime

class DatabaseManager:
    """Database manager for the crossword puzzle application"""
    
    def __init__(self, db_path='database/crossword.db'):
        """Initialize database connection"""
        self.db_path = db_path
        # Ensure database exists
        if not os.path.exists(db_path):
            # Initialize database if it doesn't exist
            self._init_db()
    
    def _get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def _init_db(self):
        """Initialize the database if it doesn't exist"""
        # Create the database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        
        print(f"Initializing database at {self.db_path}")
        
        # Import init_db script to run database setup
        try:
            import database.init_db
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            # Fallback to minimal database initialization if init_db.py fails
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create basic tables needed for the application
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
            
            # Create puzzles table (for compatibility with server.py)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS puzzles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                grid TEXT NOT NULL,
                answer TEXT NOT NULL,
                clues TEXT NOT NULL,
                times_solved INTEGER DEFAULT 0
            )
            ''')
            
            # Insert test user
            cursor.execute('''
            INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
            ''', ("admin", "admin123"))
            
            # Get the admin user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
            admin_id = cursor.fetchone()[0]
            
            # Add a simple crossword
            simple_crossword = {
                "name": "Computer Science",
                "gridSize": json.dumps([5, 5]),
                "visibleSquares": json.dumps([[0, 0], [0, 2], [0, 4], 
                                             [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
                                             [4, 0], [4, 2], [4, 4]]),
                "words": json.dumps(["CODE", "PYTHON", "DATA"]),
                "clues": json.dumps([
                    {"id": 1, "text": "What programmers write", "direction": "across", "position": [0, 0], "answer": "CODE"},
                    {"id": 2, "text": "Popular programming language", "direction": "down", "position": [2, 0], "answer": "PYTHON"},
                    {"id": 3, "text": "Information processed by computers", "direction": "across", "position": [4, 0], "answer": "DATA"}
                ]),
                "lateralWords": json.dumps({
                    "CODE": {"start": [0, 0], "end": [0, 4]},
                    "DATA": {"start": [4, 0], "end": [4, 4]}
                }),
                "verticalWords": json.dumps({
                    "PYTHON": {"start": [0, 2], "end": [4, 2]}
                })
            }
            
            cursor.execute('''
            INSERT INTO crosswords (
                name, gridSize, visibleSquares, words, clues, lateralWords, verticalWords, creator_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                simple_crossword["name"],
                simple_crossword["gridSize"],
                simple_crossword["visibleSquares"],
                simple_crossword["words"],
                simple_crossword["clues"],
                simple_crossword["lateralWords"],
                simple_crossword["verticalWords"],
                admin_id
            ))
            
            # Add sample puzzles for server.py
            from database import add_sample_puzzles
            add_sample_puzzles(cursor)
            
            conn.commit()
            conn.close()
    
    # ======= User Management =======
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, username FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def register_user(self, username, password):
        """Register a new user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            return {"user_id": cursor.lastrowid, "username": username}
        except sqlite3.IntegrityError:
            # Username already exists
            return None
        finally:
            conn.close()
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get user general stats
            cursor.execute(
                """
                SELECT id, username, puzzles_solved, puzzles_created 
                FROM users 
                WHERE id = ?
                """,
                (user_id,)
            )
            user = cursor.fetchone()
            
            if not user:
                return None
            
            # Get user best times
            cursor.execute(
                """
                SELECT b.puzzle_id, c.name, b.best_time, b.timestamp
                FROM user_best_times b
                JOIN crosswords c ON b.puzzle_id = c.id
                WHERE b.user_id = ?
                ORDER BY b.best_time ASC
                """,
                (user_id,)
            )
            best_times = [dict(row) for row in cursor.fetchall()]
            
            # Combine data
            stats = dict(user)
            stats['best_times'] = best_times
            return stats
        finally:
            conn.close()
    
    def get_all_users_stats(self):
        """Get statistics for all users"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT id, username, puzzles_solved, puzzles_created
                FROM users
                ORDER BY puzzles_solved DESC
                """
            )
            users = [dict(row) for row in cursor.fetchall()]
            return users
        finally:
            conn.close()
    
    # ======= Puzzle Management =======
    
    def get_all_puzzles(self):
        """Get all puzzles"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT c.id, c.name, u.username as creator, c.difficulty_level, 
                       c.times_solved, c.average_solve_time
                FROM crosswords c
                LEFT JOIN users u ON c.creator_id = u.id
                ORDER BY c.id DESC
                """
            )
            puzzles = [dict(row) for row in cursor.fetchall()]
            return puzzles
        finally:
            conn.close()
    
    def get_puzzle_detail(self, puzzle_id):
        """Get puzzle details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT c.*, u.username as creator_name
                FROM crosswords c
                LEFT JOIN users u ON c.creator_id = u.id
                WHERE c.id = ?
                """,
                (puzzle_id,)
            )
            puzzle = cursor.fetchone()
            
            if not puzzle:
                return None
            
            # Get leaderboard for this puzzle
            cursor.execute(
                """
                SELECT l.user_id, u.username, l.solve_time, l.timestamp
                FROM leaderboards l
                JOIN users u ON l.user_id = u.id
                WHERE l.puzzle_id = ?
                ORDER BY l.solve_time ASC
                LIMIT 10
                """,
                (puzzle_id,)
            )
            leaderboard = [dict(row) for row in cursor.fetchall()]
            
            # Convert to dictionary and add leaderboard
            puzzle_dict = dict(puzzle)
            puzzle_dict['leaderboard'] = leaderboard
            
            return puzzle_dict
        finally:
            conn.close()
    
    def create_puzzle(self, data):
        """Create a new puzzle"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate puzzle structure
            if not self._validate_puzzle_structure(data):
                return {"status": "error", "message": "Invalid puzzle structure. Words must be connected."}
            
            # Insert puzzle
            cursor.execute(
                """
                INSERT INTO crosswords (
                    name, gridSize, visibleSquares, words, clues, 
                    lateralWords, verticalWords, creator_id, difficulty_level
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data['name'],
                    data['gridSize'],
                    data['visibleSquares'],
                    data['words'],
                    data['clues'],
                    data['lateralWords'],
                    data['verticalWords'],
                    data['creator_id'],
                    data.get('difficulty_level', 'Medium')
                )
            )
            
            puzzle_id = cursor.lastrowid
            
            # Update user's puzzles_created count
            cursor.execute(
                """
                UPDATE users 
                SET puzzles_created = puzzles_created + 1 
                WHERE id = ?
                """,
                (data['creator_id'],)
            )
            
            conn.commit()
            return {"status": "ok", "puzzle_id": puzzle_id}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def _validate_puzzle_structure(self, data):
        """Validate that words in the puzzle are connected"""
        # A simplified validation - in a real implementation, this would be more complex
        # to ensure all words are connected in the grid
        
        # Check if the puzzle has both lateral and vertical words
        try:
            lateral_words = json.loads(data['lateralWords']) if isinstance(data['lateralWords'], str) else data['lateralWords']
            vertical_words = json.loads(data['verticalWords']) if isinstance(data['verticalWords'], str) else data['verticalWords']
            
            # Must have at least one word in each direction
            if not lateral_words or not vertical_words:
                return False
            
            # Check if at least one intersection exists
            for lat_word, lat_pos in lateral_words.items():
                lat_start = lat_pos['start']
                lat_end = lat_pos['end']
                
                # Check each vertical word for intersection
                for vert_word, vert_pos in vertical_words.items():
                    vert_start = vert_pos['start']
                    vert_end = vert_pos['end']
                    
                    # Check if the vertical word crosses the lateral word
                    if (vert_start[1] == vert_end[1] and  # Same column
                        lat_start[0] == lat_end[0] and    # Same row
                        vert_start[0] <= lat_start[0] <= vert_end[0] and  # Vertical covers lateral's row
                        lat_start[1] <= vert_start[1] <= lat_end[1]):     # Lateral covers vertical's column
                        return True
            
            return False
        except Exception:
            return False
    
    # ======= Solution Management =======
    
    def start_puzzle_attempt(self, user_id, puzzle_id):
        """Record the start of a puzzle attempt"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO puzzle_attempts (user_id, puzzle_id)
                VALUES (?, ?)
                """,
                (user_id, puzzle_id)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update_puzzle_progress(self, attempt_id, progress):
        """Update puzzle progress"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE puzzle_attempts
                SET progress = ?
                WHERE id = ?
                """,
                (json.dumps(progress), attempt_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def complete_puzzle_attempt(self, attempt_id, successful):
        """Complete a puzzle attempt"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now()
            
            # First get the attempt details
            cursor.execute(
                """
                SELECT user_id, puzzle_id, start_time
                FROM puzzle_attempts
                WHERE id = ?
                """,
                (attempt_id,)
            )
            attempt = cursor.fetchone()
            
            if not attempt:
                return None
            
            # Calculate duration
            start_time = datetime.strptime(attempt['start_time'], '%Y-%m-%d %H:%M:%S')
            duration = (now - start_time).total_seconds()
            
            # Update the attempt
            cursor.execute(
                """
                UPDATE puzzle_attempts
                SET end_time = ?, duration = ?, successful = ?
                WHERE id = ?
                """,
                (now.strftime('%Y-%m-%d %H:%M:%S'), duration, 1 if successful else 0, attempt_id)
            )
            
            if successful:
                user_id = attempt['user_id']
                puzzle_id = attempt['puzzle_id']
                
                # Check if this is the first solution for this user and puzzle
                cursor.execute(
                    """
                    SELECT count(*) as count
                    FROM solutions
                    WHERE user_id = ? AND puzzle_id = ?
                    """,
                    (user_id, puzzle_id)
                )
                solution_exists = cursor.fetchone()['count'] > 0
                
                if solution_exists:
                    # Update existing solution
                    cursor.execute(
                        """
                        UPDATE solutions
                        SET solve_time = CASE WHEN solve_time > ? THEN ? ELSE solve_time END,
                            attempt_count = attempt_count + 1,
                            timestamp = CASE WHEN solve_time > ? THEN datetime('now') ELSE timestamp END
                        WHERE user_id = ? AND puzzle_id = ?
                        """,
                        (duration, duration, duration, user_id, puzzle_id)
                    )
                else:
                    # Insert new solution
                    cursor.execute(
                        """
                        INSERT INTO solutions (user_id, puzzle_id, solve_time)
                        VALUES (?, ?, ?)
                        """,
                        (user_id, puzzle_id, duration)
                    )
                    
                    # Update user's puzzles_solved count
                    cursor.execute(
                        """
                        UPDATE users
                        SET puzzles_solved = puzzles_solved + 1
                        WHERE id = ?
                        """,
                        (user_id,)
                    )
                
                # Update puzzle stats
                cursor.execute(
                    """
                    UPDATE crosswords
                    SET times_solved = times_solved + CASE WHEN ? = 0 THEN 1 ELSE 0 END,
                        average_solve_time = (average_solve_time * times_solved + ?) / (times_solved + CASE WHEN ? = 0 THEN 1 ELSE 0 END)
                    WHERE id = ?
                    """,
                    (1 if solution_exists else 0, duration, 1 if solution_exists else 0, puzzle_id)
                )
                
                # Check/update user's best time
                cursor.execute(
                    """
                    SELECT count(*) as count, best_time
                    FROM user_best_times
                    WHERE user_id = ? AND puzzle_id = ?
                    """,
                    (user_id, puzzle_id)
                )
                best_time_record = cursor.fetchone()
                
                if best_time_record['count'] > 0:
                    # Update if this is better
                    if duration < best_time_record['best_time']:
                        cursor.execute(
                            """
                            UPDATE user_best_times
                            SET best_time = ?, timestamp = datetime('now')
                            WHERE user_id = ? AND puzzle_id = ?
                            """,
                            (duration, user_id, puzzle_id)
                        )
                else:
                    # Insert new best time
                    cursor.execute(
                        """
                        INSERT INTO user_best_times (user_id, puzzle_id, best_time, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                        """,
                        (user_id, puzzle_id, duration)
                    )
                
                # Add to leaderboard
                cursor.execute(
                    """
                    INSERT INTO leaderboards (puzzle_id, user_id, solve_time)
                    VALUES (?, ?, ?)
                    """,
                    (puzzle_id, user_id, duration)
                )
            
            conn.commit()
            return {"duration": duration, "successful": successful}
        finally:
            conn.close()
    
    def submit_solution(self, user_id, puzzle_id, solution):
        """Submit a solution for a puzzle"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get the puzzle
            cursor.execute(
                """
                SELECT words
                FROM crosswords
                WHERE id = ?
                """,
                (puzzle_id,)
            )
            puzzle = cursor.fetchone()
            
            if not puzzle:
                return {"status": "error", "message": "Puzzle not found"}
            
            # Check solution (simplified check)
            words = json.loads(puzzle['words']) if isinstance(puzzle['words'], str) else puzzle['words']
            solution_text = ''.join([''.join(row) for row in solution])
            
            # Simple validation - check if all words from puzzle appear in solution
            correct = all(word in solution_text for word in words)
            
            # Record an attempt
            attempt_id = self.start_puzzle_attempt(user_id, puzzle_id)
            result = self.complete_puzzle_attempt(attempt_id, correct)
            
            if correct:
                return {"status": "ok", "message": "Correct solution!", "time": result['duration']}
            else:
                return {"status": "error", "message": "Incorrect solution. Please try again."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    # ======= Leaderboard Management =======
    
    def get_leaderboards(self):
        """Get global leaderboards"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get top solvers (by number of puzzles solved)
            cursor.execute(
                """
                SELECT id, username, puzzles_solved
                FROM users
                ORDER BY puzzles_solved DESC
                LIMIT 10
                """
            )
            top_solvers = [dict(row) for row in cursor.fetchall()]
            
            # Get top creators (by number of puzzles created)
            cursor.execute(
                """
                SELECT id, username, puzzles_created
                FROM users
                ORDER BY puzzles_created DESC
                LIMIT 10
                """
            )
            top_creators = [dict(row) for row in cursor.fetchall()]
            
            # Get fastest solves
            cursor.execute(
                """
                SELECT l.puzzle_id, c.name as puzzle_name, l.user_id, u.username, 
                       l.solve_time, l.timestamp
                FROM leaderboards l
                JOIN users u ON l.user_id = u.id
                JOIN crosswords c ON l.puzzle_id = c.id
                ORDER BY l.solve_time ASC
                LIMIT 10
                """
            )
            fastest_solves = [dict(row) for row in cursor.fetchall()]
            
            return {
                "top_solvers": top_solvers,
                "top_creators": top_creators,
                "fastest_solves": fastest_solves
            }
        finally:
            conn.close()
    
    def get_puzzle_leaderboard(self, puzzle_id):
        """Get leaderboard for a specific puzzle"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT l.user_id, u.username, l.solve_time, l.timestamp
                FROM leaderboards l
                JOIN users u ON l.user_id = u.id
                WHERE l.puzzle_id = ?
                ORDER BY l.solve_time ASC
                LIMIT 10
                """,
                (puzzle_id,)
            )
            leaderboard = [dict(row) for row in cursor.fetchall()]
            return leaderboard
        finally:
            conn.close()
    
    # ======= Rating Management =======
    
    def rate_puzzle(self, user_id, puzzle_id, rating, comment=None):
        """Rate a puzzle"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO puzzle_ratings (user_id, puzzle_id, rating, comment)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, puzzle_id, rating, comment)
            )
            conn.commit()
            return {"status": "ok", "message": "Rating submitted"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
    
    def get_puzzle_ratings(self, puzzle_id):
        """Get ratings for a puzzle"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT r.rating, r.comment, r.timestamp, u.username
                FROM puzzle_ratings r
                JOIN users u ON r.user_id = u.id
                WHERE r.puzzle_id = ?
                ORDER BY r.timestamp DESC
                """,
                (puzzle_id,)
            )
            ratings = [dict(row) for row in cursor.fetchall()]
            
            # Calculate average rating
            cursor.execute(
                """
                SELECT AVG(rating) as average
                FROM puzzle_ratings
                WHERE puzzle_id = ?
                """,
                (puzzle_id,)
            )
            average = cursor.fetchone()['average']
            
            return {
                "ratings": ratings,
                "average": average,
                "count": len(ratings)
            }
        finally:
            conn.close()
