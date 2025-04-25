import socket
import json
import time
import puz
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import traceback

class CrosswordClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crossword Game")
        self.root.geometry("800x600")
        
        # Connect to server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('localhost', 8888))
            self.show_login_screen()
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot connect to server: {str(e)}")
            self.root.destroy()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def send_request(self, request_data):
        """Send a request to the server and get the response
        
        Args:
            request_data (dict): The request data to send
            
        Returns:
            dict: The response from the server
        """
        try:
            # Send the request
            self.sock.send(json.dumps(request_data).encode())
            
            # Get the response
            return self.receive_response()
        except Exception as e:
            print(f"Error in send_request: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            return {"status": "error", "message": f"Network error: {str(e)}"}
    
    def show_login_screen(self):
        """Display login screen"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        tk.Label(
            self.root,
            text="Crossword Game Login",
            font=("Helvetica", 24)
        ).pack(pady=40)
        
        # Username
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        # Login button
        tk.Button(
            self.root,
            text="Login / Register",
            command=self.login,
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=20)
        
        # Hint
        tk.Label(
            self.root,
            text="Note: New users will be automatically registered",
            font=("Helvetica", 10)
        ).pack()
    
    def login(self):
        """Handle login request"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return
        
        try:
            self.sock.send(json.dumps({
                'action': 'login',
                'username': username,
                'password': password
            }).encode())
            
            response = self.receive_response()
            
            if response['status'] == 'ok':
                self.current_user = username
                self.show_main_menu()
            else:
                messagebox.showerror("Error", response.get('message', 'Login failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
    
    def show_main_menu(self):
        """Display main menu"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Welcome message
        tk.Label(
            self.root,
            text=f"Welcome, {self.current_user}!",
            font=("Helvetica", 20)
        ).pack(pady=20)
        
        # Function buttons
        tk.Button(
            self.root,
            text="View Puzzle List",
            command=self.show_puzzle_list,
            font=("Helvetica", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)
        
        tk.Button(
            self.root,
            text="Add New Puzzle",
            command=self.show_add_puzzle,
            font=("Helvetica", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)
        
        tk.Button(
            self.root,
            text="View Statistics",
            command=self.show_statistics,
            font=("Helvetica", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)


        # Social button
        tk.Button(
            self.root,
            text="Social Menu",
            command=self.show_social_menu,
            font=("Helvetica", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

    
    def show_puzzle_list(self):
        """Show puzzle list screen"""
        self.clear_window()
        self.current_screen = 'puzzle_list'
        
        # Setup UI
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        header_frame = tk.Frame(container)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="Crossword Puzzles", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(side="left")
        
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        # Create a puzzle button
        create_btn = tk.Button(
            btn_frame,
            text="Create Puzzle",
            font=("Arial", 12),
            command=self.show_add_puzzle,
            bg="#FFC107",
            fg="black",
            padx=10,
            pady=5
        )
        create_btn.pack(side="left", padx=(0, 10))
        
        # Add back to menu button
        back_btn = tk.Button(
            btn_frame,
            text="Back to Menu",
            font=("Arial", 12),
            command=self.show_main_menu,
            bg="#FFC107",
            fg="black",
            padx=10,
            pady=5
        )
        back_btn.pack(side="left")
        
        puzzles_container = tk.Frame(container)
        puzzles_container.pack(fill="both", expand=True, pady=10)
        
        # Get puzzles from server
        response = self.send_request({'action': 'get_puzzles'})
        
        if response and response['status'] == 'ok':
            puzzles = response['puzzles']
            
            cards_per_row = 2 
            
            def resize_grid(event=None):
                nonlocal cards_per_row

                window_width = container.winfo_width()
                cards_per_row = max(1, window_width // 350)
                
                for idx, frame in enumerate(puzzle_frames):
                    row = idx // cards_per_row
                    col = idx % cards_per_row
                    frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

                for i in range(cards_per_row):
                    puzzles_container.grid_columnconfigure(i, weight=1)

            puzzle_frames = []
            
            for i, puzzle in enumerate(puzzles):

                puzzle_id = puzzle[0]
                title = puzzle[1] or f"Puzzle {puzzle_id}"
                author = puzzle[2] or 'Unknown'
                

                puzzle_frame = tk.Frame(puzzles_container, bd=1, relief=tk.SOLID, padx=10, pady=10)
                puzzle_frames.append(puzzle_frame)
                

                row = i // cards_per_row
                col = i % cards_per_row
                puzzle_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
                

                info_frame = tk.Frame(puzzle_frame)
                info_frame.pack(fill="x", side="top")
                

                description = "No description available." 
                
                title_label = tk.Label(info_frame, text=title, font=("Arial", 14, "bold"))
                title_label.pack(anchor="w")
                
                author_label = tk.Label(info_frame, text=f"By: {author}", font=("Arial", 10))
                author_label.pack(anchor="w")
                
                desc_label = tk.Label(info_frame, text=description, font=("Arial", 10), wraplength=300, justify="left")
                desc_label.pack(anchor="w", pady=(5, 0))
                
                # Button frame
                button_frame = tk.Frame(puzzle_frame)
                button_frame.pack(fill="x", side="bottom", pady=(10, 0))
                
                # Challenge mode button
                challenge_button = tk.Button(
                    button_frame,
                    text="Challenge Mode",
                    font=("Arial", 12, "bold"),
                    bg="#FFC107",
                    fg="black",
                    padx=10,
                    pady=5,
                    command=lambda pid=puzzle_id: self.start_challenge_mode(pid)
                )
                challenge_button.pack(side="left", padx=(0, 10))
                
                # Play button
                play_button = tk.Button(
                    button_frame,
                    text="Nomal Mode",
                    font=("Arial", 12),
                    bg="#FFC107",
                    fg="black",
                    padx=10,
                    pady=5,
                    command=lambda pid=puzzle_id: self.show_puzzle(pid)
                )
                play_button.pack(side="left")
            

            for i in range(cards_per_row):
                puzzles_container.grid_columnconfigure(i, weight=1)
            

            container.bind("<Configure>", resize_grid)
            

            self.root.update_idletasks()
            resize_grid()
        else:
            error_msg = "No puzzles found or server error"
            if response:
                error_msg = response.get('message', error_msg)
            error_label = tk.Label(
                container, 
                text=error_msg,
                font=("Arial", 12),
                fg="red"
            )
            error_label.pack(pady=50)
    
    def receive_response(self):
        """Receive and parse response from server"""
        try:
            data_buffer = b""
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data_buffer += chunk
                try:
                    # Try to parse the accumulated data
                    response = json.loads(data_buffer.decode())
                    if 'pending_requests' not in response:
                        response['pending_requests'] = []  # Add empty list if missing
                    return response
                except json.JSONDecodeError as e:
                    if "Unterminated string" not in str(e):
                        # If it's not an unterminated string, it's a real error
                        print(f"JSON Decode Error: {str(e)}")
                        print(f"Received data: {data_buffer.decode()}")
                        raise
                    # If it's an unterminated string, continue receiving data
                    continue
        except Exception as e:
            print(f"Error receiving response: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            raise

    def show_puzzle(self, puzzle_id, challenge_mode=False):
        """Display puzzle"""
        
        self.start_time = time.time()
        self.challenge_mode = challenge_mode
        self.challenge_time = 50  # 50 seconds for challenge mode
        self.puzzle_id = puzzle_id  # Store puzzle ID for later use

        try:
            print(f"\n=== Debug: Requesting puzzle {puzzle_id} ===")

            self.sock.send(json.dumps({
                'action': 'get_puzzle_detail',
                'puzzle_id': puzzle_id
            }).encode())
            
            print("Waiting for server response...")
            response = self.receive_response()

            
            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get puzzle details'))
                return
            
            print("\n=== Debug: Processing puzzle data ===")
            print(f"Grid: {response['grid']}")
            print(f"Clues: {response['clues']}")
            print(f"Is system puzzle: {response.get('is_system_puzzle', False)}")

            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create main frame with white background
            main_frame = tk.Frame(self.root, bg='white')
            main_frame.pack(expand=True, fill="both", padx=40, pady=40)
            
            # Create mode label
            mode_label = tk.Label(
                main_frame,
                text="CHALLENGE MODE - 50 SECONDS" if challenge_mode else "NORMAL MODE",
                font=("Helvetica", 14, "bold"),
                bg='white',
                fg='#FF5722' if challenge_mode else 'black'
            )
            mode_label.pack(pady=(0, 10))
            
            # Create grid and clues frame
            game_frame = tk.Frame(main_frame, bg='white')
            game_frame.pack(expand=True, fill="both")
            
            # Create grid frame with white background
            grid_frame = tk.Frame(game_frame, bg='white')
            grid_frame.pack(side="left", padx=20)
            
            # Parse grid data
            grid_data = response['grid']
            if isinstance(grid_data, str):
                grid_data = json.loads(grid_data)
            
            self.cells = []
            for i, row in enumerate(grid_data):
                cell_row = []

                for j, cell in enumerate(row):
                    # Create cell frame
                    cell_frame = tk.Frame(grid_frame, width=40, height=40, bg='white')
                    cell_frame.grid_propagate(False)
                    cell_frame.grid(row=i, column=j, padx=1, pady=1)
                    
                    # Create cell entry
                    is_black = False
                    if isinstance(cell, dict):
                        is_black = cell.get('is_black', False)
                    else:
                        is_black = cell == '.'
                    
                    if is_black:
                        entry = tk.Entry(cell_frame, width=2, font=("Helvetica", 20), bg='black', state="disabled")
                        entry.pack(expand=True, fill="both")
                    else:
                        entry = tk.Entry(cell_frame, width=2, font=("Helvetica", 20), bg='white', fg='black', justify='center')
                        entry.pack(expand=True, fill="both")

                        def limit_to_one_char(event, entry=entry):
                            value = entry.get()
                            if len(value) > 1:
                                entry.delete(1, tk.END)

                        entry.bind('<KeyRelease>', limit_to_one_char)

                    cell_row.append(entry)

                self.cells.append(cell_row)
            
            # Force grid frame to update
            grid_frame.update_idletasks()
            
            # Create clues frame with scrollbar
            clues_frame = tk.Frame(game_frame, bg='white')
            clues_frame.pack(side="right", padx=20, fill="both", expand=True)
            
            # Create canvas for scrollable clues
            clues_canvas = tk.Canvas(clues_frame, bg='white', highlightthickness=0)
            clues_scrollbar = tk.Scrollbar(clues_frame, orient="vertical", command=clues_canvas.yview)
            clues_content = tk.Frame(clues_canvas, bg='white')
            
            clues_content.bind(
                "<Configure>",
                lambda e: clues_canvas.configure(scrollregion=clues_canvas.bbox("all"))
            )
            
            clues_canvas.create_window((0, 0), window=clues_content, anchor="nw")
            clues_canvas.configure(yscrollcommand=clues_scrollbar.set)
            
            # Pack canvas and scrollbar
            clues_canvas.pack(side="left", fill="both", expand=True)
            clues_scrollbar.pack(side="right", fill="y")
            
            # Parse clues data
            clues_data = response['clues']
            if isinstance(clues_data, str):
                clues_data = json.loads(clues_data)
            
            is_system_puzzle = response.get('is_system_puzzle', False)
            

            # Prepare clue position maps
            across_clue_map = []
            down_clue_map = []

            for clue in clues_data['across']:
                clue_text = f"{clue['number']}. {clue['text']}"
                row = clue.get('row', 0)
                col = clue.get('col', 0)
                length = clue.get('len', 1)
                positions = [(row, col + j) for j in range(length)]
                across_clue_map.append((clue_text, positions))

            for clue in clues_data['down']:
                clue_text = f"{clue['number']}. {clue['text']}"
                row = clue.get('row', 0)
                col = clue.get('col', 0)
                length = clue.get('len', 1)
                positions = [(row + j, col) for j in range(length)]
                down_clue_map.append((clue_text, positions))

            # Define highlight function
            def highlight_cells(positions, color="#FFFACD"):
                for row in self.cells:
                    for cell in row:
                        if cell['state'] != 'disabled':
                            cell.config(bg='white')
                for r, c in positions:
                    if 0 <= r < len(self.cells) and 0 <= c < len(self.cells[r]):
                        cell = self.cells[r][c]
                        if cell['state'] != 'disabled':
                            cell.config(bg=color)

            # Display across clues
            tk.Label(
                clues_content,

                text="Across:",
                font=("Helvetica", 14, "bold"),
                bg='white',
                fg='black'
            ).pack(anchor="w", pady=(0, 5))

            for clue_text, positions in across_clue_map:
                label = tk.Label(
                    clues_content,
                    text=clue_text,

                    font=("Helvetica", 12),
                    bg='white',
                    fg='black',
                    wraplength=300,
                    justify="left"

                )
                label.pack(anchor="w", pady=2)
                label.bind("<Button-1>", lambda e, pos=positions: highlight_cells(pos))

            # Display down clues
            tk.Label(
                clues_content,

                text="Down:",
                font=("Helvetica", 14, "bold"),
                bg='white',
                fg='black'

            ).pack(anchor="w", pady=(20, 5))

            for clue_text, positions in down_clue_map:
                label = tk.Label(
                    clues_content,
                    text=clue_text,

                    font=("Helvetica", 12),
                    bg='white',
                    fg='black',
                    wraplength=300,
                    justify="left"
                )
                label.pack(anchor="w", pady=2)
                label.bind("<Button-1>", lambda e, pos=positions: highlight_cells(pos))


            # Create button frame
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(pady=20)
            
            tk.Button(
                button_frame,
                text="Submit Answer",
                command=lambda: self.submit_solution(puzzle_id),
                font=("Arial", 12),
                bg='#FFC107',
                fg='black',
                padx=10,
                pady=5
            ).pack(side="left", padx=5)
            
            tk.Button(
                button_frame,
                text="Back to List",
                command=self.show_puzzle_list,
                font=("Arial", 12),
                bg='#FFC107',
                fg='black',
                padx=10,
                pady=5
            ).pack(side="left", padx=5)
            
            # Create timer label
            self.timer_label = tk.Label(button_frame, text="Time: 0s", font=("Helvetica", 12), bg='white', fg='black')
            self.timer_label.pack(side="left", padx=10)
            
            # Start timer
            self.update_timer()
            
        except Exception as e:
            print(f"Error in show_puzzle: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def start_challenge_mode(self, puzzle_id):
        """Start a puzzle in challenge mode"""
        self.show_puzzle(puzzle_id, challenge_mode=True)
        
    def update_timer(self):
        if hasattr(self, 'start_time') and hasattr(self, 'timer_label'):

            try:
                if getattr(self, 'challenge_mode', False):
                    # Challenge mode - countdown timer
                    remaining = max(0, self.challenge_time - int(time.time() - self.start_time))
                    self.timer_label.config(text=f"Time left: {remaining}s", fg='red' if remaining < 10 else 'black')
                    
                    # Check if time's up
                    if remaining == 0:
                        self.timer_label.config(text="Time's up!", fg='red')
                        messagebox.showinfo("Challenge Failed", "Time's up! Challenge failed.")
                        self.show_puzzle_list()
                        return
                else:
                    # Normal mode - counting up
                    elapsed = int(time.time() - self.start_time)
                    self.timer_label.config(text=f"Time: {elapsed}s")
                
                self.root.after(1000, self.update_timer)
            except (AttributeError, tk.TclError):
                #  if the label does not exist or has been destroyed, stop the timer
                print("Timer stopped - widget no longer exists")
                pass
    
    def submit_solution(self, puzzle_id):
        """Submit puzzle solution to the server"""
        try:
            # Extract user solution from grid
            solution = []
            for i, row in enumerate(self.cells):
                solution_row = []
                for j, cell in enumerate(row):
                    if cell['state'] != 'disabled':
                        value = cell.get().strip().upper()
                        if value == '':
                            value = ' '  # Empty cells as spaces
                    else:
                        value = '.'  # Black cells as dots
                    solution_row.append(value)
                solution.append(solution_row)
            
            # Calculate elapsed time
            final_time = int(time.time() - self.start_time)
            
            # Send solution to server
            self.sock.send(json.dumps({
                'action': 'submit_solution',
                'username': self.current_user,
                'puzzle_id': puzzle_id,
                'solution': json.dumps(solution),
                'time_taken': final_time,
                'challenge_mode': getattr(self, 'challenge_mode', False)
            }).encode())
            
            response = self.receive_response()
            
            if response.get('status') == 'ok':
                challenge_success = ""
                if getattr(self, 'challenge_mode', False):
                    challenge_success = "\n\n🏆 CHALLENGE MODE COMPLETED! 🏆"
                
                # If there's rank information in the response, show it
                if 'rank' in response and 'total_solvers' in response:
                    message = (f"Congratulations! Correct solution!{challenge_success}\n\n"
                               f"Your time: {int(final_time//60)}:{int(final_time%60):02d}\n"
                               f"Your rank: {response['rank']} of {response['total_solvers']}")
                    
                    # Add medal emoji based on rank
                    if response['rank'] == 1:
                        message += "\n\n🥇 You have the fastest time!"
                    elif response['rank'] == 2:
                        message += "\n\n🥈 You have the second fastest time!"
                    elif response['rank'] == 3:
                        message += "\n\n🥉 You have the third fastest time!"
                    
                    messagebox.showinfo("Success", message)
                else:
                    messagebox.showinfo("Success", f"Correct solution!{challenge_success}")
                    
                # Return to the puzzle list
                self.show_puzzle_list()
            else:
                messagebox.showerror("Error", response.get('message', 'Unknown error'))
                # Continue the timer
                self.start_time = time.time() - final_time  # Adjust start time to keep elapsed time constant
                
        except Exception as e:
            print(f"Error in submit_solution: {str(e)}")
            print("Full error:")
            traceback.print_exc()
            messagebox.showerror("Error", f"Network error: {str(e)}")
    
    def show_add_puzzle(self):
        """Display add puzzle interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)
        
        # Create top frame for title, import button and return button

        top_frame = tk.Frame(main_frame, bg='white')
        top_frame.pack(fill="x", pady=10)
        
        # Title
        tk.Label(
            top_frame,
            text="Add New Puzzle",
            font=("Helvetica", 20),
            bg='white',
            fg='black'
        ).pack(side="left", padx=20)
        
        # Return button at top
        tk.Button(
            top_frame,
            text="Back to Menu",
            command=self.show_main_menu,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(side="right", padx=20)
        

        # Create content frame
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(expand=True, fill="both", padx=20)

        # Left side - Grid controls and grid
        left_frame = tk.Frame(content_frame, bg='white')
        left_frame.pack(side="left", fill="both", expand=True)

        # Title input
        title_frame = tk.Frame(left_frame, bg='white')
        title_frame.pack(fill="x", pady=5)
        tk.Label(title_frame, text="Title:", font=("Helvetica", 12), bg='white').pack(side="left", padx=5)
        title_entry = tk.Entry(title_frame, font=("Helvetica", 12), width=30)
        title_entry.pack(side="left", expand=True, fill="x", padx=5)

        # Grid size controls
        size_frame = tk.Frame(left_frame, bg='white')
        size_frame.pack(fill="x", pady=10)
        
        tk.Label(size_frame, text="Grid Size:", font=("Helvetica", 12), bg='white').pack(side="left", padx=5)
        size_var = tk.StringVar(value="3x3")
        sizes = ["3x3", "4x4", "5x5", "6x6", "7x7", "8x8", "9x9", "10x10"]  # Define sizes here
        size_menu = tk.OptionMenu(size_frame, size_var, *sizes)
        size_menu.config(font=("Helvetica", 12), bg='white')
        size_menu.pack(side="left", padx=5)

        # Grid frame
        grid_frame = tk.Frame(left_frame, bg='white')
        grid_frame.pack(pady=10)

        # Grid cells storage
        cells = []
        current_size = [3, 3]  # Default size

        def create_grid(rows, cols):
            nonlocal cells
            # Clear existing grid
            for widget in grid_frame.winfo_children():
                widget.destroy()
            
            cells = []
            for i in range(rows):
                row_cells = []
                for j in range(cols):
                    cell_frame = tk.Frame(grid_frame, width=40, height=40)
                    cell_frame.grid_propagate(False)
                    cell_frame.grid(row=i, column=j, padx=1, pady=1)

                    entry = tk.Entry(cell_frame, width=2, font=("Helvetica", 20), 
                                   bg='white', fg='black', justify='center')
                    entry.pack(expand=True, fill="both")

                    def limit_to_one_char(event, entry=entry):
                        value = entry.get()
                        if len(value) > 1:
                            entry.delete(1, tk.END)

                    entry.bind('<KeyRelease>', limit_to_one_char)

                    row_cells.append(entry)
                cells.append(row_cells)

        def update_grid_size(*args):
            size = size_var.get()
            rows, cols = map(int, size.split('x'))
            current_size[0], current_size[1] = rows, cols
            create_grid(rows, cols)

        size_var.trace('w', update_grid_size)

        # Right side - Clues input with scroll support
        right_container = tk.Frame(content_frame, bg='white')
        right_container.pack(side="right", fill="both", expand=True, padx=(20, 0))

        right_canvas = tk.Canvas(right_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(right_container, orient="vertical", command=right_canvas.yview)
        scrollable_frame = tk.Frame(right_canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        right_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=scrollbar.set)

        right_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right_frame = scrollable_frame

        # Clues frame
        clues_frame = tk.Frame(right_frame, bg='white')
        clues_frame.pack(fill="both", expand=True)

        # Across clues
        across_frame = tk.Frame(clues_frame, bg='white')
        across_frame.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(across_frame, text="Across Clues:", font=("Helvetica", 14, "bold"), 
                bg='white').pack(anchor="w")

        across_clues_frame = tk.Frame(across_frame, bg='white')
        across_clues_frame.pack(fill="both", expand=True)

        # Down clues
        down_frame = tk.Frame(clues_frame, bg='white')
        down_frame.pack(fill="both", expand=True)

        tk.Label(down_frame, text="Down Clues:", font=("Helvetica", 14, "bold"), 
                bg='white').pack(anchor="w")

        down_clues_frame = tk.Frame(down_frame, bg='white')
        down_clues_frame.pack(fill="both", expand=True)

        across_entries = []
        down_entries = []

        def add_clue_entry(parent_frame, entries_list):
            num = len(entries_list) + 1
            frame = tk.Frame(parent_frame, bg='white')
            frame.pack(fill="x", pady=2)
            
            tk.Label(frame, text=f"{num}.", font=("Helvetica", 12), 
                    bg='white', width=3).pack(side="left")
            entry = tk.Entry(frame, font=("Helvetica", 12), width=40)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            
            entries_list.append(entry)

        def add_across_clue():
            add_clue_entry(across_clues_frame, across_entries)

        def add_down_clue():
            add_clue_entry(down_clues_frame, down_entries)

        # Add clue buttons
        tk.Button(across_frame, text="Add Across Clue", command=add_across_clue,
                 font=("Arial", 10), bg='#FFC107', fg='black', padx=10, pady=5).pack(pady=5)
        
        tk.Button(down_frame, text="Add Down Clue", command=add_down_clue,
                 font=("Arial", 10), bg='#FFC107', fg='black', padx=10, pady=5).pack(pady=5)

        # Create initial grid
        create_grid(3, 3)
        
        # Add initial clue entries
        add_across_clue()
        add_down_clue()

        def import_puz_file():
            """Import and display PUZ file content in the grid editor"""
            across_clue_map = []
            down_clue_map = []

            file_path = filedialog.askopenfilename(filetypes=[("PUZ files", "*.puz")])
            if not file_path:
                return
            
            try:
                puzzle = puz.read(file_path)
                numbering = puzzle.clue_numbering()
                print(f"Debug: Found {len(numbering.across)} across and {len(numbering.down)} down clues")

                # Update grid size based on puzzle dimensions
                height = min(10, puzzle.height)
                width = min(10, puzzle.width)

                # Update current_size and size_var
                current_size[0], current_size[1] = height, width
                size_var.set(f"{height}x{width}")
                create_grid(height, width)

                # If original size exceeds limit, show info but don't error
                if puzzle.height > 10 or puzzle.width > 10:
                    messagebox.showinfo("Size Limitation",
                        f"Imported puzzle is {puzzle.width}x{puzzle.height}. "
                        "Only the top-left 10x10 section will be used.")

                # Clear existing clues
                for widget in across_clues_frame.winfo_children():
                    widget.destroy()
                for widget in down_clues_frame.winfo_children():
                    widget.destroy()
                across_entries.clear()
                down_entries.clear()

                # Fill the grid
                for y in range(height):
                    for x in range(width):
                        i = y * puzzle.width + x  # Keep original width to avoid misalignment
                        if i >= len(puzzle.solution):  # Prevent index out of range
                            continue
                        
                        char = puzzle.solution[i]
                        is_black = puzzle.fill[i] == '.'
                        
                        cell = cells[y][x]
                        if is_black:
                            cell.delete(0, tk.END)
                            cell.config(state='disabled', bg='black')
                            cell.master.config(bg='black')  # Make frame black too
                        else:
                            cell.config(state='normal', bg='white')
                            cell.master.config(bg='white')
                            cell.delete(0, tk.END)
                            cell.insert(0, char)

                # Across Clues
                for entry in numbering.across:
                    cell_index = entry['cell']
                    row = cell_index // puzzle.width
                    col = cell_index % puzzle.width

                    if row < height and col < width:
                        add_clue_entry(across_clues_frame, across_entries)
                        clue_text = puzzle.clues[entry['clue_index']]
                        across_entries[-1].insert(0, clue_text)

                        positions = [(row, col + i) for i in range(entry['len']) if col + i < width]
                        across_clue_map.append((across_entries[-1], positions))

                # Down Clues
                for entry in numbering.down:
                    cell_index = entry['cell']
                    row = cell_index // puzzle.width
                    col = cell_index % puzzle.width

                    if row < height and col < width:
                        add_clue_entry(down_clues_frame, down_entries)
                        clue_text = puzzle.clues[entry['clue_index']]
                        down_entries[-1].insert(0, clue_text)

                        positions = [(row + i, col) for i in range(entry['len']) if row + i < height]
                        down_clue_map.append((down_entries[-1], positions))


                # Set title
                title_entry.delete(0, tk.END)
                title_entry.insert(0, puzzle.title or "Untitled PUZ")

                messagebox.showinfo("Success", "PUZ file loaded successfully!")
            
            except Exception as e:
                print(f"Error parsing PUZ file: {str(e)}")
                traceback.print_exc()  # Print full stack trace
                messagebox.showerror("Error", f"Failed to parse PUZ file:\n{e}")

            def highlight_cells(cells, positions, color="#FFFFCC"):
                for row in cells:
                    for cell in row:
                        if cell['state'] != 'disabled':
                            cell.config(bg='white')
                for r, c in positions:
                    if 0 <= r < len(cells) and 0 <= c < len(cells[r]):
                        cell = cells[r][c]
                        if cell['state'] != 'disabled':
                            cell.config(bg=color)

            for entry_widget, positions in across_clue_map:
                entry_widget.bind("<Button-1>", lambda e, pos=positions: highlight_cells(cells, pos))

            for entry_widget, positions in down_clue_map:
                entry_widget.bind("<Button-1>", lambda e, pos=positions: highlight_cells(cells, pos))

        # Import PUZ button in top frame
        tk.Button(
            top_frame,
            text="Import PUZ File",
            command=import_puz_file,  # Now import_puz_file is accessible
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(side="left", padx=20)

        def validate_and_submit():
            """Validate input and submit puzzle"""
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Please enter a title")
                return

            # Collect grid and answer
            grid_data = []
            answer_data = []
            rows, cols = current_size
            
            for i in range(rows):
                grid_row = []
                answer_row = []
                for j in range(cols):
                    cell = cells[i][j]
                    value = cell.get().strip().upper()
                    is_black = cell['state'] == 'disabled'
                    
                    if not is_black and not value:
                        messagebox.showerror("Error", "Please fill in all white cells")
                        return
                    
                    grid_row.append({
                        "char": value if not is_black else "",
                        "is_black": is_black
                    })
                    answer_row.append(value if not is_black else "")
                grid_data.append(grid_row)
                answer_data.append(answer_row)

            # Collect clues
            across_clues = []
            for i, entry in enumerate(across_entries):
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("Error", f"Please fill in across clue {i+1}")
                    return
                across_clues.append({"number": i+1, "text": text})

            down_clues = []
            for i, entry in enumerate(down_entries):
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("Error", f"Please fill in down clue {i+1}")
                    return
                down_clues.append({"number": i+1, "text": text})

            clues_data = {
                "across": across_clues,
                "down": down_clues
            }

            try:
                print("\n=== Debug: Preparing puzzle data ===")
                
                # Convert data to JSON strings
                grid_json = json.dumps(grid_data)
                answer_json = json.dumps(answer_data)
                clues_json = json.dumps(clues_data)
                
                print(f"Grid JSON type: {type(grid_json)}")
                print(f"Answer JSON type: {type(answer_json)}")
                print(f"Clues JSON type: {type(clues_json)}")
                
                request_data = {
                    'action': 'add_puzzle',
                    'title': title,
                    'author': self.current_user,
                    'grid': grid_json,
                    'answer': answer_json,
                    'clues': clues_json
                }
                
                print("\nFinal request data:")
                print(json.dumps(request_data, indent=2))
                
                print("\nSending data to server...")
                self.sock.send(json.dumps(request_data).encode())
                
                print("Waiting for server response...")
                response = json.loads(self.sock.recv(4096).decode())
                print(f"Server response: {response}")
                
                if response['status'] == 'ok':
                    messagebox.showinfo("Success", "Puzzle added successfully!")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Error", response.get('message', 'Failed to add puzzle'))
                    
            except Exception as e:

                print(f"\nError in validate_and_submit: {str(e)}")
                print("Full error:")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Network error: {str(e)}")

        # Submit button
        submit_frame = tk.Frame(left_frame, bg='white')
        submit_frame.pack(pady=20)

        tk.Button(
            submit_frame,
            text="Submit",
            command=validate_and_submit,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(side="left", padx=5)

    
    def show_statistics(self):
        """Display statistics"""
        try:
            self.sock.send(json.dumps({
                'action': 'get_statistics',
                'username': self.current_user
            }).encode())
            
            response = self.receive_response()
            
            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get statistics'))
                return
            
            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create main frame
            main_frame = tk.Frame(self.root)
            main_frame.pack(expand=True, fill="both", padx=40, pady=20)
            
            # Create top frame for title and return button
            top_frame = tk.Frame(main_frame, bg='white')
            top_frame.pack(fill="x", pady=10)
            
            # Title
            tk.Label(
                top_frame,
                text="User Statistics",
                font=("Helvetica", 20),
                bg='white',
                fg='black'
            ).pack(side="left", padx=20)
            
            # Return button at top
            tk.Button(
                top_frame,
                text="Back to Menu",
                command=self.show_main_menu,
                font=("Arial", 12),
                bg='#FFC107',
                fg='black',
                padx=10,
                pady=5
            ).pack(side="right", padx=20)
            
            # Create scrollable area
            canvas = tk.Canvas(main_frame, bg='white')
            scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Display current user's statistics
            current_user_frame = tk.Frame(scrollable_frame, bg='white')
            current_user_frame.pack(fill="x", pady=10)
            
            tk.Label(
                current_user_frame,
                text="Your Statistics",
                font=("Helvetica", 16, "bold"),
                bg='white',
                fg='black'
            ).pack(anchor='w', pady=5)
            
            current_stats = response['current_user_stats']
            tk.Label(
                current_user_frame,
                text=f"Puzzles Solved: {current_stats['puzzles_solved']}\n"
                     f"Puzzles Created: {current_stats['puzzles_created']}",
                font=("Helvetica", 12),
                bg='white',
                fg='black',
                justify=tk.LEFT
            ).pack(anchor='w', padx=20)
            
            latest_time = current_stats.get('latest_time')
            if latest_time is not None:
                tk.Label(
                    current_user_frame,
                    text=f"Time Spent on Last Puzzle: {latest_time} seconds",
                    font=("Helvetica", 12),
                    bg='white',
                    fg='black',
                    justify=tk.LEFT
                ).pack(anchor='w', padx=20, pady=5)

            # Display leaderboard
            tk.Label(
                scrollable_frame,
                text="Leaderboard",
                font=("Helvetica", 16, "bold"),
                bg='white',
                fg='black'
            ).pack(pady=20)
            
            # Create table headers
            headers_frame = tk.Frame(scrollable_frame, bg='white')
            headers_frame.pack(fill="x", padx=20)

            tk.Label(
                headers_frame,
                text="Username",
                font=("Helvetica", 12, "bold"),
                width=20,
                bg='white',
                fg='black'
            ).pack(side="left")
            
            tk.Label(
                headers_frame,
                text="Puzzles Solved",
                font=("Helvetica", 12, "bold"),
                width=15,
                bg='white',
                fg='black'
            ).pack(side="left")
            
            tk.Label(
                headers_frame,
                text="Fastest Time (s)",
                font=("Helvetica", 12, "bold"),
                width=15,
                bg='white',
                fg='black'
            ).pack(side="left")

            tk.Label(
                headers_frame,
                text="Average Time (s)",
                font=("Helvetica", 12, "bold"),
                width=15,
                bg='white',
                fg='black'
            ).pack(side="left")

            tk.Label(
                headers_frame,
                text="Puzzles Created",
                font=("Helvetica", 12, "bold"),
                width=15,
                bg='white',
                fg='black'
            ).pack(side="left")
            
            # Display all users' statistics
            for user_stats in response['all_users_stats']:
                user_frame = tk.Frame(scrollable_frame, bg='white')
                user_frame.pack(fill="x", padx=20)

                tk.Label(
                    user_frame,
                    text=user_stats['username'],
                    font=("Helvetica", 12),
                    width=20,
                    bg='white',
                    fg='black'
                ).pack(side="left")
                
                tk.Label(
                    user_frame,
                    text=str(user_stats['puzzles_solved']),
                    font=("Helvetica", 12),
                    width=15,
                    bg='white',
                    fg='black'
                ).pack(side="left")
                
                tk.Label(
                    user_frame,
                    text=str(user_stats.get('fastest_time', 'N/A')),
                    font=("Helvetica", 12),
                    width=15,
                    bg='white',
                    fg='black'
                ).pack(side="left")

                tk.Label(
                    user_frame,
                    text=str(user_stats.get('average_time', 'N/A')),
                    font=("Helvetica", 12),
                    width=15,
                    bg='white',
                    fg='black'
                ).pack(side="left")

                tk.Label(
                    user_frame,
                    text=str(user_stats['puzzles_created']),
                    font=("Helvetica", 12),
                    width=15,
                    bg='white',
                    fg='black'
                ).pack(side="left")
            
            # Add button to view historical rankings
            view_button = tk.Button(self.root, text="View Historical Rankings", 
                                   command=self.show_historical_rankings)
            view_button.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def show_historical_rankings(self):
        """Show historical rankings for the current user"""
        # Clear main window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create header
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=10)
        
        tk.Label(header_frame, text="Historical Rankings", font=("Arial", 18, "bold")).pack()
        
        # Create back button
        back_button = tk.Button(header_frame, text="Back to Statistics", 
                                command=self.show_statistics)
        back_button.pack(pady=5)
        
        # Create main content frame with scrollbar
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add a canvas for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Request historical rankings from server
        request = {
            'action': 'get_historical_rankings',
            'username': self.username if hasattr(self, 'username') else self.current_user
        }
        
        response = self.send_request(request)
        
        if response.get('status') == 'ok' and 'records' in response:
            records = response['records']
            
            # Create header row
            header_row = tk.Frame(scrollable_frame)
            header_row.pack(fill="x", pady=5)
            
            headers = ["Puzzle", "Time", "Date", "Rank", "Total Solvers"]
            widths = [200, 100, 100, 80, 100]
            
            for i, header in enumerate(headers):
                tk.Label(header_row, text=header, width=widths[i]//10, 
                         font=("Arial", 10, "bold")).pack(side="left", padx=5)
            
            # Add separator
            separator = ttk.Separator(scrollable_frame, orient='horizontal')
            separator.pack(fill='x', pady=5)
            
            if not records:
                tk.Label(scrollable_frame, text="No puzzles solved yet!", 
                         font=("Arial", 12)).pack(pady=20)
            else:
                # Add record rows
                for record in records:
                    row = tk.Frame(scrollable_frame)
                    row.pack(fill="x", pady=2)
                    
                    # Format time as minutes:seconds
                    minutes = int(record['time_taken']) // 60
                    seconds = int(record['time_taken']) % 60
                    time_str = f"{minutes}:{seconds:02d}"
                    
                    # Format date
                    date_str = record['solved_at'].split(' ')[0]
                    
                    # Format rank
                    rank_str = f"{record['rank']} of {record['total_solvers']}"
                    
                    # Set color based on rank
                    rank_color = "#000000"  # Default black
                    if record['rank'] == 1:
                        rank_color = "#FFD700"  # Gold
                    elif record['rank'] == 2:
                        rank_color = "#C0C0C0"  # Silver
                    elif record['rank'] == 3:
                        rank_color = "#CD7F32"  # Bronze
                    
                    # Add each cell
                    tk.Label(row, text=record['puzzle_title'], width=widths[0]//10,
                             anchor="w").pack(side="left", padx=5)
                    tk.Label(row, text=time_str, width=widths[1]//10).pack(side="left", padx=5)
                    tk.Label(row, text=date_str, width=widths[2]//10).pack(side="left", padx=5)
                    tk.Label(row, text=record['rank'], width=widths[3]//10,
                             fg=rank_color).pack(side="left", padx=5)
                    tk.Label(row, text=record['total_solvers'], width=widths[4]//10).pack(side="left", padx=5)
                    
                    # Add light separator
                    separator = ttk.Separator(scrollable_frame, orient='horizontal')
                    separator.pack(fill='x', pady=2)
        else:
            error_msg = response.get('message', 'Unknown error')
            tk.Label(scrollable_frame, text=f"Error: {error_msg}", 
                     font=("Arial", 12), fg="red").pack(pady=20)
        
        # Add button to view historical rankings
        view_button = tk.Button(self.root, text="Refresh Rankings", 
                               command=self.show_historical_rankings)
        view_button.pack(pady=10)

    def show_social_menu(self):
        """Display social menu for adding friends, viewing friends, sending messages"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="Social Menu",
            font=("Helvetica", 24)
        ).pack(pady=40)

        # Add Friend button
        tk.Button(
            self.root,
            text="Add Friend",
            command=self.show_add_friend,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

        # View Friend Requests button
        tk.Button(
            self.root,
            text="View Friend Requests",
            command=self.show_friend_requests,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

        # View Friends button
        tk.Button(
            self.root,
            text="View Friends",
            command=self.show_friends_list,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

        # Send Message button
        tk.Button(
            self.root,
            text="Send Message",
            command=self.show_send_message,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

        # View Messages button
        tk.Button(
            self.root,
            text="View Messages",
            command=self.show_view_messages,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

        # Back to Menu button
        tk.Button(
            self.root,
            text="Back to Menu",
            command=self.show_main_menu,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(side="right", padx=20)

    def show_add_friend(self):
        """Display add friend interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="Add Friend",
            font=("Arial", 24)
        ).pack(pady=40)

        # Friend username input
        tk.Label(self.root, text="Friend's Username:").pack()
        self.friend_username_entry = tk.Entry(self.root)
        self.friend_username_entry.pack(pady=5)

        # Add Friend button
        tk.Button(
            self.root,
            text="Send Friend Request",
            command=self.add_friend,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=20)

        # Back to Menu button
        tk.Button(
            self.root,
            text="Back to Menu",
            command=self.show_main_menu,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

    def add_friend(self):
        """Send friend request to server"""
        friend_username = self.friend_username_entry.get()
        if not friend_username:
            messagebox.showerror("Error", "Please enter a friend's username")
            return

        try:
            request_data = {
                'action': 'add_friend',
                'user_id': self.current_user,
                'friend_id': friend_username
            }

            print(f"Debug: Sending friend request - {request_data}")  # Debug log
            self.sock.send(json.dumps(request_data).encode())

            response = self.receive_response()

            print(f"Debug: Received response - {response}")  # Debug log

            if response['status'] == 'ok':
                messagebox.showinfo("Success", "Friend request sent!")
            else:
                messagebox.showerror("Error", response.get('message', 'Failed to send friend request'))
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def show_friends_list(self):
        """Display list of friends"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="Friends List",
            font=("Helvetica", 24)
        ).pack(pady=40)

        try:
            self.sock.send(json.dumps({
                'action': 'get_friends',
                'user_id': self.current_user
            }).encode())

            response = self.receive_response()

            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get friends list'))
                return

            # Display friends list
            friends_frame = tk.Frame(self.root)
            friends_frame.pack(expand=True, fill="both", padx=40, pady=40)

            for friend in response['friends']:
                tk.Label(friends_frame, text=friend, font=("Helvetica", 12)).pack(pady=5)

            # Back to Menu button
            tk.Button(
                self.root,
                text="Back to Menu",
                command=self.show_main_menu,
                font=("Arial", 12),
                bg='#FFC107',
                fg='black',
                padx=10,
                pady=5
            ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def show_send_message(self):
        """Display send message interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="Send Message",
            font=("Helvetica", 24)
        ).pack(pady=40)

        # Friend username input
        tk.Label(self.root, text="Friend's Username:").pack()
        self.message_friend_username_entry = tk.Entry(self.root)
        self.message_friend_username_entry.pack(pady=5)

        # Message input
        tk.Label(self.root, text="Message:").pack()
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.pack(pady=5)

        # Send Message button
        tk.Button(
            self.root,
            text="Send Message",
            command=self.send_message,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=20)

        # Back to Menu button
        tk.Button(
            self.root,
            text="Back to Menu",
            command=self.show_main_menu,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=10)

    def send_message(self):
        """Send message to friend"""
        friend_username = self.message_friend_username_entry.get()
        message = self.message_entry.get()

        if not friend_username or not message:
            messagebox.showerror("Error", "Both fields are required")
            return

        try:
            self.sock.send(json.dumps({
                'action': 'send_message',
                'sender_id': self.current_user,
                'receiver_id': friend_username,
                'message': message
            }).encode())
            
            response = self.receive_response()
            
            if response['status'] == 'ok':
                messagebox.showinfo("Success", "Message sent!")
            else:
                messagebox.showerror("Error", response.get('message', 'Failed to send message'))
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def show_friend_requests(self):
        """Display all pending friend requests"""
        try:
            self.sock.send(json.dumps({
                'action': 'get_friend_requests',
                'user_id': self.current_user
            }).encode())

            response = self.receive_response()
            print(f"Debug: Received pending friend requests response - {response}")  # Debug log

            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get friend requests'))
                return

            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Title
            tk.Label(
                self.root,
                text="Pending Friend Requests",
                font=("Helvetica", 24)
            ).pack(pady=40)

            # Display pending requests
            if response['pending_requests']:
                for request in response['pending_requests']:
                    sender_id = request['user_id']  # This is the user who sent the request

                    tk.Label(
                        self.root,
                        text=f"{sender_id} wants to add you as a friend",
                        font=("Helvetica", 14)
                    ).pack(pady=10)

                    # Accept button
                    tk.Button(
                        self.root,
                        text=f"Accept {sender_id}",
                        command=lambda sender_id=sender_id: self.accept_friend_request(sender_id),
                        font=("Arial", 12),
                        bg='#FFC107',
                        fg='black',
                        padx=10,
                        pady=5
                    ).pack(pady=5)

                    # Reject button
                    tk.Button(
                        self.root,
                        text=f"Reject {sender_id}",
                        command=lambda sender_id=sender_id: self.reject_friend_request(sender_id),
                        font=("Arial", 12),
                        bg='#FFC107',
                        fg='black',
                        padx=10,
                        pady=5
                    ).pack(pady=5)
            else:
                # Show message when there are no pending requests
                tk.Label(
                    self.root,
                    text="No pending friend requests",
                    font=("Helvetica", 14)
                ).pack(pady=20)

            # Always show Back to Menu button
            tk.Button(
                self.root,
                text="Back to Menu",
                command=self.show_main_menu,
                font=("Arial", 12),
                bg='#FFC107',
                fg='black',
                padx=10,
                pady=5
            ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def accept_friend_request(self, friend_id):
        """Accept a friend request"""
        try:
            self.sock.send(json.dumps({
                'action': 'confirm_friend',
                'user_id': self.current_user,
                'friend_id': friend_id
            }).encode())
            
            response = self.receive_response()
            
            if response['status'] == 'ok':
                messagebox.showinfo("Success", f"You are now friends with {friend_id}")
                self.show_main_menu()  # Return to the main menu
            else:
                messagebox.showerror("Error", response.get('message', 'Failed to confirm friend request'))
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def reject_friend_request(self, friend_id):
        """Reject a friend request"""
        try:
            self.sock.send(json.dumps({
                'action': 'reject_friend',
                'user_id': self.current_user,
                'friend_id': friend_id
            }).encode())
            
            response = self.receive_response()
            
            if response['status'] == 'ok':
                messagebox.showinfo("Success", f"You rejected the friend request from {friend_id}")
                self.show_main_menu()  # Return to the main menu
            else:
                messagebox.showerror("Error", response.get('message', 'Failed to reject friend request'))
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

    def show_view_messages(self):
        """Display message history with friends"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="View Messages",
            font=("Helvetica", 24)
        ).pack(pady=20)

        try:
            # First get the friends list
            self.sock.send(json.dumps({
                'action': 'get_friends',
                'user_id': self.current_user
            }).encode())

            response = self.receive_response()

            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get friends list'))
                return

            friends = response['friends']

            if not friends:
                tk.Label(
                    self.root,
                    text="You don't have any friends yet",
                    font=("Helvetica", 14)
                ).pack(pady=20)
            else:
                # Create a frame for the messages area
                messages_frame = tk.Frame(self.root)
                messages_frame.pack(fill="both", expand=True, padx=20, pady=20)

                # Create a canvas with scrollbar for the messages
                canvas = tk.Canvas(messages_frame, bg='white')
                scrollbar = tk.Scrollbar(messages_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg='white')

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                # For each friend, get and display messages
                for friend in friends:
                    # Create a frame for this friend's messages
                    friend_frame = tk.Frame(scrollable_frame, bg='white')
                    friend_frame.pack(fill="x", pady=10)

                    tk.Label(
                        friend_frame,
                        text=f"Messages with {friend}:",
                        font=("Helvetica", 12, "bold"),
                        bg='white'
                    ).pack(anchor="w")

                    # Get messages with this friend
                    self.sock.send(json.dumps({
                        'action': 'get_messages',
                        'user_id': self.current_user,
                        'friend_id': friend
                    }).encode())

                    msg_response = self.receive_response()

                    if msg_response['status'] == 'ok':
                        messages = msg_response['messages']
                        if messages:
                            for msg in messages:
                                sender = msg['sender_id']
                                message = msg['message']
                                timestamp = msg['timestamp']
                                
                                # Format the message
                                if sender == self.current_user:
                                    prefix = "You: "
                                    bg_color = '#E3F2FD'  # Light blue for sent messages
                                else:
                                    prefix = f"{sender}: "
                                    bg_color = '#F5F5F5'  # Light grey for received messages

                                # Create message bubble
                                msg_frame = tk.Frame(friend_frame, bg=bg_color)
                                msg_frame.pack(fill="x", pady=2, padx=10)
                                
                                tk.Label(
                                    msg_frame,
                                    text=f"{prefix}{message}",
                                    wraplength=400,
                                    justify="left",
                                    bg=bg_color,
                                    padx=10,
                                    pady=5
                                ).pack(anchor="w")
                        else:
                            tk.Label(
                                friend_frame,
                                text="No messages yet",
                                font=("Helvetica", 10),
                                bg='white'
                            ).pack(pady=5)

                # Pack the canvas and scrollbar
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

        # Back to Social Menu button
        tk.Button(
            self.root,
            text="Back to Social Menu",
            command=self.show_social_menu,
            font=("Arial", 12),
            bg='#FFC107',
            fg='black',
            padx=10,
            pady=5
        ).pack(pady=20)

if __name__ == "__main__":
    CrosswordClient()
