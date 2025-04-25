import socket
import threading
import json
import sqlite3
import traceback
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
        
        # Sync crosswords to puzzles table
        self._sync_crosswords_to_puzzles()
        
        print(f"Server started, listening on port {self.port}...")
    
    def _sync_crosswords_to_puzzles(self):
        """Sync data from crosswords table to puzzles table"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get all crosswords
            cursor.execute("""
                SELECT id, name, creator_id, gridSize, clues, words 
                FROM crosswords
            """)
            crosswords = cursor.fetchall()
            
            for cw in crosswords:
                # Get creator username
                cursor.execute("SELECT username FROM users WHERE id = ?", (cw['creator_id'],))
                creator = cursor.fetchone()
                author = creator['username'] if creator else 'system'
                
                # Check if puzzle already exists
                cursor.execute("SELECT id FROM puzzles WHERE id = ?", (cw['id'],))
                if cursor.fetchone() is None:
                    # Convert data format to match puzzles table
                    grid = json.loads(cw['gridSize']) if isinstance(cw['gridSize'], str) else cw['gridSize']
                    clues = json.loads(cw['clues']) if isinstance(cw['clues'], str) else cw['clues']
                    words = json.loads(cw['words']) if isinstance(cw['words'], str) else cw['words']
                    
                    # Create a simple grid for the puzzle format
                    formatted_grid = []
                    grid_width = int(grid[0])
                    grid_height = int(grid[1])
                    
                    for i in range(grid_height):
                        row = []
                        for j in range(grid_width):
                            row.append(" ")
                        formatted_grid.append(row)
                    
                    # Insert into puzzles
                    cursor.execute("""
                        INSERT INTO puzzles (id, title, author, grid, answer, clues)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        cw['id'], 
                        cw['name'], 
                        author,
                        json.dumps(formatted_grid),
                        json.dumps(formatted_grid),  # Answer initially matches grid
                        json.dumps(clues)
                    ))
            
            conn.commit()
            print(f"Synced {len(crosswords)} crosswords to puzzles table.")
        except Exception as e:
            print(f"Error syncing crosswords: {str(e)}")
            traceback.print_exc()
        finally:
            conn.close()
    
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
                # preprocess JSON data
                if 'grid' in request:
                    try:
                        if isinstance(request['grid'], str):
                            json.loads(request['grid'])  # verify JSON string
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
            elif action == 'add_friend':
                return self.handle_add_friend(request)
            elif action == 'confirm_friend':
                return self.handle_confirm_friend(request)
            elif action == 'send_message':
                return self.handle_send_message(request)
            elif action == 'get_messages':
                return self.handle_get_messages(request)
            elif action == 'get_friend_requests':
                return self.handle_get_friend_requests(request)
            elif action == 'get_friends':
                return self.handle_get_friends(request)
            elif action == 'reject_friend':
                return self.handle_reject_friend(request)
            elif action == 'get_historical_rankings':
                return self.handle_get_historical_rankings(request)
            else:
                print(f"Debug: Unknown action type received: {action}")
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
            raw_puzzles = cursor.fetchall()
            
            # Convert Row objects to list of tuples for JSON serialization
            puzzles = []
            for puzzle in raw_puzzles:
                puzzles.append((puzzle['id'], puzzle['title'], puzzle['author']))
                
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
            
            # 首先检查puzzles表中的数据
            cursor.execute(
                "SELECT grid, clues, author FROM puzzles WHERE id = ?",
                (puzzle_id,)
            )
            result = cursor.fetchone()

            if result:
                try:
                    raw_grid = result[0]
                    raw_clues = result[1]
                    author = result[2]
                    
                    print("\nRaw data from database:")
                    print(f"Grid: {raw_grid[:100]}...")
                    print(f"Clues: {raw_clues[:100]}...")
                    print(f"Author: {author}")
                    
                    # Parse grid data
                    try:
                        if isinstance(raw_grid, str):
                            grid = json.loads(raw_grid)
                        else:
                            grid = raw_grid
                        print("\nParsed grid successfully")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing grid: {str(e)}")
                        return {'status': 'error', 'message': f'Invalid grid format: {str(e)}'}

                    # Parse clues data
                    try:
                        if isinstance(raw_clues, str):
                            clues = json.loads(raw_clues)
                        else:
                            clues = raw_clues
                        
                        # 如果clues是空的，尝试从crosswords表获取
                        if (not isinstance(clues, dict)) or (not clues.get('across') and not clues.get('down')):
                            print("Clues data empty or invalid, attempting to get from crosswords table")
                            cursor.execute(
                                "SELECT clues FROM crosswords WHERE id = ?",
                                (puzzle_id,)
                            )
                            crossword_result = cursor.fetchone()
                            if crossword_result:
                                raw_crossword_clues = crossword_result[0]
                                if isinstance(raw_crossword_clues, str):
                                    crossword_clues = json.loads(raw_crossword_clues)
                                else:
                                    crossword_clues = raw_crossword_clues
                                
                                # 转换为客户端期望的格式
                                formatted_clues = {"across": [], "down": []}
                                for clue in crossword_clues:
                                    if clue.get('direction') == 'across':
                                        formatted_clues['across'].append({
                                            'number': clue.get('id', 1),
                                            'text': clue.get('text', 'No clue text'),
                                            'row': clue.get('position', [0, 0])[0],
                                            'col': clue.get('position', [0, 0])[1],
                                            'len': len(clue.get('answer', '')) if 'answer' in clue else 5
                                        })
                                    elif clue.get('direction') == 'down':
                                        formatted_clues['down'].append({
                                            'number': clue.get('id', 1),
                                            'text': clue.get('text', 'No clue text'),
                                            'row': clue.get('position', [0, 0])[0],
                                            'col': clue.get('position', [0, 0])[1],
                                            'len': len(clue.get('answer', '')) if 'answer' in clue else 5
                                        })
                                
                                clues = formatted_clues
                                
                                # 更新puzzles表中的clues
                                cursor.execute(
                                    "UPDATE puzzles SET clues = ? WHERE id = ?",
                                    (json.dumps(clues), puzzle_id)
                                )
                                conn.commit()
                        
                        # Ensure clues has the correct structure
                        if not isinstance(clues, dict):
                            clues = {"across": [], "down": []}
                        if "across" not in clues:
                            clues["across"] = []
                        if "down" not in clues:
                            clues["down"] = []
                            
                        print("\nParsed clues successfully")
                        print(f"Clues structure: {json.dumps(clues, indent=2)[:200]}...")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing clues: {str(e)}")
                        return {'status': 'error', 'message': f'Invalid clues format: {str(e)}'}

                    # Add default clues for sample puzzles if empty
                    if len(clues["across"]) == 0 and len(clues["down"]) == 0:
                        # Computer Science Basics
                        if puzzle_id == 1:
                            clues = {
                                "across": [
                                    {"number": 1, "text": "Foundation of computer science and programming", "row": 0, "col": 0, "len": 5},
                                    {"number": 2, "text": "Memory used to speed up data access", "row": 2, "col": 0, "len": 5},
                                    {"number": 3, "text": "Find and fix errors in code", "row": 4, "col": 0, "len": 5}
                                ],
                                "down": [
                                    {"number": 1, "text": "A data structure that stores elements of the same type", "row": 0, "col": 0, "len": 5},
                                    {"number": 2, "text": "A blueprint for creating objects in OOP", "row": 0, "col": 2, "len": 5}
                                ]
                            }
                        # Artificial Intelligence
                        elif puzzle_id == 2:
                            clues = {
                                "across": [
                                    {"number": 1, "text": "Neural network type used for image processing", "row": 0, "col": 0, "len": 3},
                                    {"number": 2, "text": "Machine processing of human languages", "row": 1, "col": 1, "len": 3}
                                ],
                                "down": [
                                    {"number": 1, "text": "Popular generative AI model family", "row": 0, "col": 0, "len": 3},
                                    {"number": 2, "text": "Deep Neural Network", "row": 0, "col": 3, "len": 3}
                                ]
                            }
                        # St Andrews, Scotland
                        elif puzzle_id == 3:
                            clues = {
                                "across": [
                                    {"number": 1, "text": "St Andrews has ruins of a medieval one", "row": 0, "col": 0, "len": 6},
                                    {"number": 2, "text": "Harbor structure in St Andrews", "row": 2, "col": 2, "len": 4},
                                    {"number": 3, "text": "The famous '___ Course' in St Andrews", "row": 5, "col": 3, "len": 3}
                                ],
                                "down": [
                                    {"number": 1, "text": "What many have done on the Old Course", "row": 0, "col": 3, "len": 6},
                                    {"number": 2, "text": "North ___, body of water beside St Andrews", "row": 2, "col": 5, "len": 3}
                                ]
                            }
                        
                        # 更新puzzles表中的clues
                        cursor.execute(
                            "UPDATE puzzles SET clues = ? WHERE id = ?",
                            (json.dumps(clues), puzzle_id)
                        )
                        conn.commit()

                    # Check if this is a system puzzle
                    is_system_puzzle = author == 'system'
                    grid_height = len(grid)
                    grid_width = len(grid[0]) if grid_height > 0 else 0

                    if is_system_puzzle:
                        # For system puzzles, use simple row/column based positioning
                        print("\nProcessing system puzzle...")
                        
                        # Process across clues
                        for i, clue in enumerate(clues['across']):
                            if isinstance(clue, dict):
                                clue['row'] = i
                                clue['col'] = 0
                                clue['len'] = grid_width
                            else:
                                # Convert string clues to dict format
                                clues['across'][i] = {
                                    'number': i + 1,
                                    'text': clue,
                                    'row': i,
                                    'col': 0,
                                    'len': grid_width
                                }
                        
                        # Process down clues
                        for i, clue in enumerate(clues['down']):
                            if isinstance(clue, dict):
                                clue['row'] = 0
                                clue['col'] = i
                                clue['len'] = grid_height
                            else:
                                # Convert string clues to dict format
                                clues['down'][i] = {
                                    'number': i + 1,
                                    'text': clue,
                                    'row': 0,
                                    'col': i,
                                    'len': grid_height
                                }
                    else:
                        # For imported PUZ files, calculate positions based on black squares
                        print("\nProcessing imported PUZ puzzle...")
                        
                        # Process across clues
                        for i, clue in enumerate(clues['across']):
                            if not isinstance(clue, dict):
                                clues['across'][i] = {
                                    'number': i + 1,
                                    'text': clue
                                }
                            if 'number' not in clues['across'][i]:
                                clues['across'][i]['number'] = i + 1
                        
                        # Process down clues
                        for i, clue in enumerate(clues['down']):
                            if not isinstance(clue, dict):
                                clues['down'][i] = {
                                    'number': i + 1,
                                    'text': clue
                                }
                            if 'number' not in clues['down'][i]:
                                clues['down'][i]['number'] = i + 1
                        
                        # Calculate positions for imported puzzles
                        self._calculate_imported_puzzle_positions(grid, clues)

                    response = {
                        'status': 'ok',
                        'grid': grid,
                        'clues': clues,
                        'is_system_puzzle': is_system_puzzle
                    }
                    
                    print("\nFinal response:")
                    print(json.dumps(response, indent=2)[:200] + "...")
                    
                    return response
                    
                except Exception as e:
                    print(f"Error processing puzzle data: {str(e)}")
                    print("Full error:")
                    import traceback
                    traceback.print_exc()
                    return {'status': 'error', 'message': f'Error processing puzzle: {str(e)}'}
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

    def _calculate_imported_puzzle_positions(self, grid, clues):
        """Calculate positions for imported puzzle clues"""
        grid_height = len(grid)
        grid_width = len(grid[0]) if grid_height > 0 else 0
        
        # Calculate cell numbers
        cell_numbers = {}
        number = 1
        for row in range(grid_height):
            for col in range(grid_width):
                cell = grid[row][col]
                is_black = False
                if isinstance(cell, dict):
                    is_black = cell.get('is_black', False)
                else:
                    is_black = cell == '.'
                
                if not is_black:
                    needs_number = False
                    # Check if start of across word
                    if col == 0 or (isinstance(grid[row][col-1], dict) and grid[row][col-1].get('is_black', True)):
                        needs_number = True
                    # Check if start of down word
                    if row == 0 or (isinstance(grid[row-1][col], dict) and grid[row-1][col].get('is_black', True)):
                        needs_number = True
                    
                    if needs_number:
                        cell_numbers[(row, col)] = number
                        number += 1
        
        # Process across clues
        for clue in clues['across']:
            if isinstance(clue, dict) and 'number' in clue:
                # Find matching cell number
                for (row, col), num in cell_numbers.items():
                    if num == clue['number']:
                        # Calculate length
                        length = 0
                        while col + length < grid_width:
                            next_cell = grid[row][col + length]
                            if isinstance(next_cell, dict):
                                if next_cell.get('is_black', False):
                                    break
                            elif next_cell == '.':
                                break
                            length += 1
                        
                        clue['row'] = row
                        clue['col'] = col
                        clue['len'] = length
                        break
        
        # Process down clues
        for clue in clues['down']:
            if isinstance(clue, dict) and 'number' in clue:
                # Find matching cell number
                for (row, col), num in cell_numbers.items():
                    if num == clue['number']:
                        # Calculate length
                        length = 0
                        while row + length < grid_height:
                            next_cell = grid[row + length][col]
                            if isinstance(next_cell, dict):
                                if next_cell.get('is_black', False):
                                    break
                            elif next_cell == '.':
                                break
                            length += 1
                        
                        clue['row'] = row
                        clue['col'] = col
                        clue['len'] = length
                        break

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
                    # Calculate the rank among all solvers of this puzzle
                    cursor.execute(
                        """
                        SELECT COUNT(*) + 1 as rank FROM puzzle_records 
                        WHERE puzzle_id = ? AND time_taken < ?
                        """,
                        (puzzle_id, time_taken)
                    )
                    rank_result = cursor.fetchone()
                    rank = rank_result[0] if rank_result else 1
                    
                    # Get total number of solvers for this puzzle
                    cursor.execute(
                        "SELECT COUNT(*) as total FROM puzzle_records WHERE puzzle_id = ?",
                        (puzzle_id,)
                    )
                    total_result = cursor.fetchone()
                    total_solvers = total_result[0] if total_result else 0
                    
                    # Insert into puzzle_records
                    cursor.execute(
                        "INSERT INTO puzzle_records (username, puzzle_id, time_taken) VALUES (?, ?, ?)",
                        (username, puzzle_id, time_taken)
                    )
                    
                    # Insert into historical_rankings
                    cursor.execute(
                        """
                        INSERT INTO historical_rankings 
                        (user_id, puzzle_id, score, rank, timestamp)
                        VALUES (?, ?, ?, ?, datetime('now'))
                        """,
                        (username, puzzle_id, time_taken, rank)
                    )

                conn.commit()
                
                # Return rank information with the response
                if time_taken is not None:
                    return {
                        'status': 'ok', 
                        'message': 'Correct answer!',
                        'rank': rank,
                        'total_solvers': total_solvers + 1  # Add 1 to include this solution
                    }
                else:
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
    
    def handle_send_message(self, request):
        """Handle sending a message from one user to another"""
        try:
            sender_id = request['sender_id']
            receiver_id = request['receiver_id']
            message = request['message']

            if not sender_id or not receiver_id or not message:
                return {'status': 'error', 'message': 'sender_id, receiver_id, and message are required'}

            # Save the message to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                (sender_id, receiver_id, message)
            )
            conn.commit()
            conn.close()

            return {'status': 'ok', 'message': 'Message sent successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


    def handle_add_friend(self, request):
        """Handle adding a friend (send friend request)"""
        try:
            user_id = request['user_id']
            friend_id = request['friend_id']

            print(f"\nDebug: Processing friend request from {user_id} to {friend_id}")

            if not user_id or not friend_id:
                return {'status': 'error', 'message': 'Both user_id and friend_id are required'}

            # Check if the user and friend exist in the database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (user_id,))
            user = cursor.fetchone()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (friend_id,))
            friend = cursor.fetchone()

            if not user:
                return {'status': 'error', 'message': 'User does not exist'}
            if not friend:
                return {'status': 'error', 'message': 'Friend does not exist'}

            # Check if friend request already exists
            cursor.execute(
                "SELECT status FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                print(f"Debug: Existing friend request found with status: {existing[0]}")
                if existing[0] == 'pending':
                    return {'status': 'error', 'message': 'Friend request already sent'}
                elif existing[0] == 'confirmed':
                    return {'status': 'error', 'message': 'Already friends'}

            # Add the friend request to the database
            cursor.execute(
                "INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'pending')",
                (user_id, friend_id)
            )
            conn.commit()
            
            # Debug log to confirm data insertion
            print(f"Debug: Friend request added - {user_id} -> {friend_id}, status: pending")
            
            # Verify the insertion
            cursor.execute(
                "SELECT * FROM friends WHERE user_id = ? AND friend_id = ?",
                (user_id, friend_id)
            )
            result = cursor.fetchone()
            print(f"Debug: Verification - Friend request in database: {result}")
                  
            conn.close()

            return {'status': 'ok', 'message': 'Friend request sent'}
        except Exception as e:
            print(f"Debug: Error in handle_add_friend: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def handle_confirm_friend(self, request):
        """Handle confirming a friend request"""
        try:
            user_id = request['user_id']  # B
            friend_id = request['friend_id']  # A

            print(f"\nDebug: Confirming friend request between {user_id} and {friend_id}")

            if not user_id or not friend_id:
                return {'status': 'error', 'message': 'Both user_id and friend_id are required'}

            # Confirm the friend request in the database by updating the status to 'confirmed'
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First, verify that there is a pending friend request
            cursor.execute(
                "SELECT * FROM friends WHERE user_id = ? AND friend_id = ? AND status = 'pending'",
                (friend_id, user_id)  # A -> B (original request)
            )
            pending_request = cursor.fetchone()
            
            if not pending_request:
                conn.close()
                return {'status': 'error', 'message': 'No pending friend request found'}
            
            # Update the original friend request (A -> B)
            cursor.execute(
                "UPDATE friends SET status = 'confirmed' WHERE user_id = ? AND friend_id = ?",
                (friend_id, user_id)  # A -> B
            )
            
            # Add the reverse friendship (B -> A)
            cursor.execute(
                "INSERT OR REPLACE INTO friends (user_id, friend_id, status) VALUES (?, ?, 'confirmed')",
                (user_id, friend_id)  # B -> A
            )
            
            conn.commit()
            
            # Debug: Verify the friendship status
            cursor.execute("""
                SELECT user_id, friend_id, status 
                FROM friends 
                WHERE (user_id = ? AND friend_id = ?) 
                   OR (user_id = ? AND friend_id = ?)
            """, (user_id, friend_id, friend_id, user_id))
            
            friendship_records = cursor.fetchall()
            print(f"Debug: Friendship records after confirmation: {friendship_records}")
            
            conn.close()

            return {'status': 'ok', 'message': f'{friend_id} confirmed as a friend of {user_id}'}
        except Exception as e:
            print(f"Debug: Error in handle_confirm_friend: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        
    def handle_get_friends(self, request):
        """Handle fetching the user's friends list"""
        try:
            user_id = request['user_id']

            print(f"\nDebug: Fetching friends list for user {user_id}")

            if not user_id:
                return {'status': 'error', 'message': 'user_id is required'}

            # Fetch the friends from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get friends in both directions (where user is either user_id or friend_id)
            # Use DISTINCT to prevent duplicates
            cursor.execute("""
                SELECT DISTINCT
                    CASE 
                        WHEN user_id = ? THEN friend_id 
                        WHEN friend_id = ? THEN user_id 
                    END as friend
                FROM friends 
                WHERE (user_id = ? OR friend_id = ?) 
                AND status = 'confirmed'
            """, (user_id, user_id, user_id, user_id))
            
            friends = cursor.fetchall()
            
            # Debug log
            print(f"Debug: Found friends for {user_id}: {friends}")
            
            conn.close()

            # Extract friend usernames from query results and remove duplicates using set
            friend_list = list(set([friend[0] for friend in friends if friend[0] is not None]))
            
            # Debug log
            print(f"Debug: Processed friend list: {friend_list}")

            return {'status': 'ok', 'friends': friend_list}
        except Exception as e:
            print(f"Debug: Error in handle_get_friends: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def handle_get_friend_requests(self, request):
        """Handle fetching all pending friend requests for a user"""
        try:
            user_id = request['user_id']

            print(f"\nDebug: Fetching friend requests for user {user_id}")

            if not user_id:
                return {'status': 'error', 'message': 'user_id is required'}

            # Retrieve pending friend requests for the user
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Debug: Show all friend records for this user
            cursor.execute("SELECT * FROM friends WHERE friend_id = ?", (user_id,))
            all_records = cursor.fetchall()
            print(f"Debug: All friend records for {user_id}: {all_records}")
            
            cursor.execute(
                "SELECT user_id, friend_id FROM friends WHERE friend_id = ? AND status = 'pending'",
                (user_id,)
            )
            pending_requests = cursor.fetchall()
            
            # Debug log to show the pending requests
            print(f"Debug: Retrieved pending friend requests for {user_id}: {pending_requests}")

            conn.close()

            # Return the pending friend requests
            return {
                'status': 'ok',
                'pending_requests': [{'user_id': req[0], 'friend_id': req[1]} for req in pending_requests]
            }
        except Exception as e:
            print(f"Debug: Error in handle_get_friend_requests: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def handle_get_messages(self, request):
        """Handle fetching all messages between two users"""
        try:
            user_id = request['user_id']
            friend_id = request['friend_id']

            print(f"\nDebug: Fetching messages between {user_id} and {friend_id}")

            if not user_id or not friend_id:
                return {'status': 'error', 'message': 'Both user_id and friend_id are required'}

            # Check if they are friends
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM friends 
                WHERE ((user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?))
                AND status = 'confirmed'
            """, (user_id, friend_id, friend_id, user_id))
            
            friendship = cursor.fetchone()
            
            if not friendship:
                conn.close()
                return {'status': 'error', 'message': 'You can only view messages with your friends'}

            # Retrieve messages between user_id and friend_id
            # Use DISTINCT to prevent duplicates and order by timestamp
            cursor.execute("""
                SELECT DISTINCT sender_id, receiver_id, message, timestamp 
                FROM messages 
                WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) 
                ORDER BY timestamp
            """, (user_id, friend_id, friend_id, user_id))
            
            messages = cursor.fetchall()
            
            print(f"Debug: Found {len(messages)} messages")
            
            conn.close()

            # Return the messages
            return {
                'status': 'ok',
                'messages': [{'sender_id': msg[0], 'receiver_id': msg[1], 'message': msg[2], 'timestamp': msg[3]} for msg in messages]
            }
        except Exception as e:
            print(f"Debug: Error in handle_get_messages: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def handle_get_historical_rankings(self, request):
        """Handle fetching historical rankings for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            username = request.get('username')
            
            if not username:
                return {'status': 'error', 'message': 'Username is required'}
            
            # Get user's historical puzzle records with ranking information
            cursor.execute("""
                WITH RankedRecords AS (
                    SELECT 
                        pr1.username,
                        pr1.puzzle_id,
                        p.title as puzzle_title,
                        pr1.time_taken,
                        pr1.solved_at,
                        (SELECT COUNT(*) + 1 FROM puzzle_records pr2 
                         WHERE pr2.puzzle_id = pr1.puzzle_id AND pr2.time_taken < pr1.time_taken) as rank,
                        (SELECT COUNT(*) FROM puzzle_records pr3 
                         WHERE pr3.puzzle_id = pr1.puzzle_id) as total_solvers
                    FROM puzzle_records pr1
                    JOIN puzzles p ON pr1.puzzle_id = p.id
                    WHERE pr1.username = ?
                )
                SELECT * FROM RankedRecords
                ORDER BY solved_at DESC
            """, (username,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'username': row[0],
                    'puzzle_id': row[1],
                    'puzzle_title': row[2],
                    'time_taken': row[3],
                    'solved_at': row[4],
                    'rank': row[5],
                    'total_solvers': row[6]
                })
            
            # Also save these records in the historical_rankings table
            for record in records:
                cursor.execute("""
                    INSERT OR IGNORE INTO historical_rankings 
                    (user_id, puzzle_id, score, rank, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, record['puzzle_id'], record['time_taken'], 
                      record['rank'], record['solved_at']))
            
            conn.commit()
            
            return {
                'status': 'ok',
                'records': records
            }
        except Exception as e:
            print(f"Error in handle_get_historical_rankings: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()


if __name__ == "__main__":
    server = CrosswordServer()
    server.start()