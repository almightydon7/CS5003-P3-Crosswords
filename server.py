# server.py
import socket
import threading
import json
import sqlite3
from database import init_db, get_db_connection

class CrosswordServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Initialize database
        init_db()
        
        print(f"Server started, listening on port {self.port}...")
    
    def start(self):
        """Start server and accept client connections"""
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Accepted connection from {address}")
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.start()
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            while True:
                data = client_socket.recv(4096).decode()
                if not data:
                    break
                    
                request = json.loads(data)
                response = self.process_request(request)
                client_socket.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"Error handling client request: {str(e)}")
        finally:
            client_socket.close()
    
    def process_request(self, request):
        """Process client request"""
        action = request.get('action')
        
        if action == 'login':
            return self.handle_login(request)
        elif action == 'register':
            return self.handle_register(request)
        elif action == 'get_puzzles':
            return self.handle_get_puzzles()
        elif action == 'get_puzzle_detail':
            return self.handle_get_puzzle_detail(request)
        elif action == 'submit_solution':
            return self.handle_submit_solution(request)
        elif action == 'add_puzzle':
            return self.handle_add_puzzle(request)
        elif action == 'get_statistics':
            return self.handle_get_statistics(request)
        else:
            return {'status': 'error', 'message': 'Unknown action type'}
    
    def handle_login(self, request):
        """Handle login request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            username = request['username']
            password = request['password']
            
            cursor.execute(
                "SELECT password FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            
            if result is None:
                # New user, auto register
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                return {'status': 'ok', 'message': 'New user registered successfully'}
            
            if result[0] == password:
                return {'status': 'ok', 'message': 'Login successful'}
            else:
                return {'status': 'error', 'message': 'Incorrect password'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def handle_get_puzzles(self):
        """Get puzzle list"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, title, author FROM puzzles ORDER BY id DESC"
            )
            puzzles = cursor.fetchall()
            return {'status': 'ok', 'puzzles': puzzles}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def handle_get_puzzle_detail(self, request):
        """Get puzzle details"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            puzzle_id = request['puzzle_id']
            cursor.execute(
                "SELECT grid, clues FROM puzzles WHERE id = ?",
                (puzzle_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'status': 'ok',
                    'grid': result[0],
                    'clues': result[1]
                }
            else:
                return {'status': 'error', 'message': 'Puzzle not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def handle_submit_solution(self, request):
        """Handle submitted answer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            username = request['username']
            puzzle_id = request['puzzle_id']
            submitted_solution = json.loads(request['solution'])
            
            # Get correct answer
            cursor.execute(
                "SELECT answer FROM puzzles WHERE id = ?",
                (puzzle_id,)
            )
            result = cursor.fetchone()
            if not result:
                return {'status': 'error', 'message': 'Puzzle not found'}
            
            correct_answer = json.loads(result[0])
            
            # Validate answer
            is_correct = True
            for i in range(len(correct_answer)):
                for j in range(len(correct_answer[i])):
                    if submitted_solution[i][j].upper() != correct_answer[i][j].upper():
                        is_correct = False
                        break
                if not is_correct:
                    break
            
            if is_correct:
                # Update user's solved puzzles count
                cursor.execute(
                    "UPDATE users SET puzzles_solved = puzzles_solved + 1 WHERE username = ?",
                    (username,)
                )
                
                # Update puzzle solve count
                cursor.execute(
                    "UPDATE puzzles SET times_solved = times_solved + 1 WHERE id = ?",
                    (puzzle_id,)
                )
                
                conn.commit()
                return {'status': 'ok', 'message': 'Correct answer!'}
            else:
                return {'status': 'error', 'message': 'Incorrect answer, please try again'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def handle_add_puzzle(self, request):
        """Add new puzzle"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            title = request['title']
            author = request['author']
            grid = request['grid']
            answer = request['answer']
            clues = request['clues']
            
            cursor.execute(
                """
                INSERT INTO puzzles (title, author, grid, answer, clues)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, author, grid, answer, clues)
            )
            
            # Update user's created puzzles count
            cursor.execute(
                "UPDATE users SET puzzles_created = puzzles_created + 1 WHERE username = ?",
                (author,)
            )
            
            conn.commit()
            return {'status': 'ok', 'message': 'Puzzle added successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

    def handle_get_statistics(self, request):
        """Get statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            username = request.get('username')
            
            # Get current user's statistics
            cursor.execute("""
                SELECT puzzles_solved, puzzles_created 
                FROM users 
                WHERE username = ?
            """, (username,))
            
            user_row = cursor.fetchone()
            current_user_stats = {
                'puzzles_solved': user_row[0] if user_row else 0,
                'puzzles_created': user_row[1] if user_row else 0
            }
            
            # Get all users' statistics
            cursor.execute("""
                SELECT username, puzzles_solved, puzzles_created 
                FROM users 
                ORDER BY puzzles_solved DESC, puzzles_created DESC
            """)
            
            all_users_stats = []
            for row in cursor.fetchall():
                user_stats = {
                    'username': row[0],
                    'puzzles_solved': row[1],
                    'puzzles_created': row[2]
                }
                all_users_stats.append(user_stats)
            
            return {
                'status': 'ok',
                'current_user_stats': current_user_stats,
                'all_users_stats': all_users_stats
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()

if __name__ == "__main__":
    server = CrosswordServer()
    server.start()