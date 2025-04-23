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
                # Initialize buffer for data collection
                data_buffer = b""
                
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        return
                    
                    data_buffer += chunk
                    
                    try:
                        # Try to decode and parse the accumulated data
                        request = json.loads(data_buffer.decode())
                        break  # Successfully parsed JSON
                    except json.JSONDecodeError as e:
                        if "Unterminated string" not in str(e):
                            # If it's not an unterminated string, it's a real error
                            print(f"JSON Decode Error: {str(e)}")
                            print(f"Received data: {data_buffer.decode()}")
                            # Send error response
                            error_response = json.dumps({
                                'status': 'error',
                                'message': f'Invalid JSON format: {str(e)}'
                            })
                            client_socket.send(error_response.encode())
                            continue
                        # If it's an unterminated string, continue receiving data
                        continue
                
                if not data_buffer:
                    break
                
                print("\n=== Debug: Processing client request ===")
                print(f"Received data length: {len(data_buffer)}")
                print(f"Request: {request}")
                
                # Process the request
                try:
                    response = self.process_request(request)
                    
                    # Ensure response is properly formatted
                    if not isinstance(response, dict):
                        response = {
                            'status': 'error',
                            'message': 'Invalid server response format'
                        }
                    
                    # Convert response to JSON string
                    response_json = json.dumps(response)
                    
                    print("\nSending response:")
                    print(f"Response length: {len(response_json)}")
                    print(f"Response preview: {response_json[:200]}...")
                    
                    # Send response
                    client_socket.send(response_json.encode())
                    
                except Exception as e:
                    print(f"Error processing request: {str(e)}")
                    print("Full error:")
                    import traceback
                    traceback.print_exc()
                    
                    error_response = json.dumps({
                        'status': 'error',
                        'message': f'Server error: {str(e)}'
                    })
                    client_socket.send(error_response.encode())
                
        except Exception as e:
            print(f"Connection error: {str(e)}")
            print("Full error:")
            import traceback
            traceback.print_exc()
        finally:
            client_socket.close()
    
    def process_request(self, request):
        """Process client request"""
        try:
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
                # 预处理 JSON 数据
                if 'grid' in request:
                    try:
                        if isinstance(request['grid'], str):
                            json.loads(request['grid'])  # 验证 JSON 字符串
                    except json.JSONDecodeError:
                        request['grid'] = json.dumps(request['grid'])
                
                if 'answer' in request:
                    try:
                        if isinstance(request['answer'], str):
                            json.loads(request['answer'])
                    except json.JSONDecodeError:
                        request['answer'] = json.dumps(request['answer'])
                
                if 'clues' in request:
                    try:
                        if isinstance(request['clues'], str):
                            json.loads(request['clues'])
                    except json.JSONDecodeError:
                        request['clues'] = json.dumps(request['clues'])
                
                return self.handle_add_puzzle(request)
            elif action == 'get_statistics':
                return self.handle_get_statistics(request)
            else:
                return {'status': 'error', 'message': 'Unknown action type'}
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
    
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
            print(f"\n=== Debug: Getting puzzle details for ID {puzzle_id} ===")
            
            cursor.execute(
                "SELECT grid, clues FROM puzzles WHERE id = ?",
                (puzzle_id,)
            )
            result = cursor.fetchone()

            if result:
                try:
                    raw_grid = result[0]
                    raw_clues = result[1]
                    
                    print("Raw data from database:")
                    print(f"Grid: {raw_grid[:100]}...")
                    print(f"Clues: {raw_clues[:100]}...")
                    
                    # Ensure grid is valid JSON
                    if isinstance(raw_grid, str):
                        grid = json.loads(raw_grid)
                    else:
                        grid = raw_grid
                        
                    # Ensure clues is valid JSON
                    if isinstance(raw_clues, str):
                        clues = json.loads(raw_clues)
                    else:
                        clues = raw_clues

                    response = {
                        'status': 'ok',
                        'grid': grid,
                        'clues': clues
                    }
                    
                    print("\nProcessed response:")
                    print(json.dumps(response, indent=2)[:200] + "...")
                    
                    return response
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {str(e)}")
                    return {'status': 'error', 'message': f'Invalid puzzle data format: {str(e)}'}
            else:
                return {'status': 'error', 'message': 'Puzzle not found'}
        except Exception as e:
            print(f"Error in handle_get_puzzle_detail: {str(e)}")
            print("Full error:")
            import traceback
            traceback.print_exc()
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

                time_taken = request.get('time_taken', None)

                cursor.execute(
                    "UPDATE users SET puzzles_solved = puzzles_solved + 1 WHERE username = ?",
                    (username,)
                )
                
                # Update puzzle solve count
                cursor.execute(
                    "UPDATE puzzles SET times_solved = times_solved + 1 WHERE id = ?",
                    (puzzle_id,)
                )
                
                if time_taken is not None:
                    cursor.execute(
                        "INSERT INTO puzzle_records (username, puzzle_id, time_taken) VALUES (?, ?, ?)",
                        (username, puzzle_id, time_taken)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            print("\n=== Debug: Processing add puzzle request ===")
            print(f"Raw request data: {request}")
            
            title = request['title']
            author = request['author']
            grid = request['grid']
            answer = request['answer']
            clues = request['clues']

            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Grid type: {type(grid)}")
            print(f"Answer type: {type(answer)}")
            print(f"Clues type: {type(clues)}")

            # Ensure they are all stringified JSON
            try:
                # First try to parse if they're JSON strings
                json.loads(grid)
                json.loads(answer)
                json.loads(clues)
            except json.JSONDecodeError:
                # If they're not already JSON strings, convert them
                if not isinstance(grid, str):
                    grid = json.dumps(grid)
                if not isinstance(answer, str):
                    answer = json.dumps(answer)
                if not isinstance(clues, str):
                    clues = json.dumps(clues)

            print("\nValidated data:")
            print(f"Grid: {grid[:100]}...")
            print(f"Answer: {answer[:100]}...")
            print(f"Clues: {clues[:100]}...")

            cursor.execute(
                """
                INSERT INTO puzzles (title, author, grid, answer, clues)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, author, grid, answer, clues)
            )
            
            cursor.execute(
                "UPDATE users SET puzzles_created = puzzles_created + 1 WHERE username = ?",
                (author,)
            )
            
            conn.commit()
            print("\nSuccessfully added puzzle to database")
            return {'status': 'ok', 'message': 'Puzzle added successfully'}
        except Exception as e:
            print(f"\nError in handle_add_puzzle: {str(e)}")
            print("Full error:")
            import traceback
            traceback.print_exc()
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

            cursor.execute("""
                SELECT time_taken FROM puzzle_records 
                WHERE username = ? 
                ORDER BY solved_at DESC 
                LIMIT 1
            """, (username,))
            latest_time_row = cursor.fetchone()
            current_user_stats['latest_time'] = latest_time_row[0] if latest_time_row else None

            # Get all users' statistics
            cursor.execute("""
                SELECT username, puzzles_solved, puzzles_created 
                FROM users 
                ORDER BY puzzles_solved DESC, puzzles_created DESC
            """)
            user_rows = cursor.fetchall()

            cursor.execute("""
                SELECT username, MIN(time_taken) 
                FROM puzzle_records 
                GROUP BY username
            """)
            fastest_times = dict(cursor.fetchall())

            cursor.execute("""
                SELECT username, AVG(time_taken)
                FROM puzzle_records
                GROUP BY username
            """)
            average_times = dict(cursor.fetchall())

            all_users_stats = []
            for row in user_rows:
                fastest = fastest_times.get(row[0])
                average = average_times.get(row[0])

                user_stats = {
                    'username': row[0],
                    'puzzles_solved': row[1],
                    'fastest_time': round(fastest, 2) if fastest is not None else "N/A",
                    'average_time': round(average, 2) if average is not None else "N/A",
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