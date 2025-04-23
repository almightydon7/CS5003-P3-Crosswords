import socket
import json
import time
import tkinter as tk
from tkinter import messagebox

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
            fg='black'
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
            
            response = json.loads(self.sock.recv(4096).decode())
            
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
            bg='#2196F3',
            fg='black'
        ).pack(pady=10)
        
        tk.Button(
            self.root,
            text="Add New Puzzle",
            command=self.show_add_puzzle,
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='black'
        ).pack(pady=10)
        
        tk.Button(
            self.root,
            text="View Statistics",
            command=self.show_statistics,
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='black'
        ).pack(pady=10)
    
    def show_puzzle_list(self):
        """Display puzzle list"""
        try:
            self.sock.send(json.dumps({'action': 'get_puzzles'}).encode())
            response = json.loads(self.sock.recv(4096).decode())
            
            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get puzzle list'))
                return
            
            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create main frame
            main_frame = tk.Frame(self.root, bg='white')
            main_frame.pack(expand=True, fill="both", padx=40, pady=40)
            
            # Title
            tk.Label(
                main_frame,
                text="Available Puzzles",
                font=("Helvetica", 20),
                bg='white',
                fg='black'
            ).pack(pady=20)
            
            # Puzzle list
            for puzzle_id, title, author in response['puzzles']:
                puzzle_frame = tk.Frame(main_frame, bg='white')
                puzzle_frame.pack(fill="x", pady=5)
                
                tk.Label(
                    puzzle_frame,
                    text=f"{title} (by: {author})",
                    font=("Helvetica", 12),
                    bg='white',
                    fg='black'
                ).pack(side="left", padx=5)
                
                tk.Button(
                    puzzle_frame,
                    text="Solve",
                    command=lambda pid=puzzle_id: self.show_puzzle(pid),
                    font=("Helvetica", 12),
                    bg='#2196F3',
                    fg='black'
                ).pack(side="right", padx=5)
            
            # Return button
            tk.Button(
                main_frame,
                text="Back to Menu",
                command=self.show_main_menu,
                font=("Helvetica", 12),
                bg='#2196F3',
                fg='black'
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
    
    def show_puzzle(self, puzzle_id):
        """Display puzzle"""
        
        self.start_time = time.time()

        try:
            self.sock.send(json.dumps({
                'action': 'get_puzzle_detail',
                'puzzle_id': puzzle_id
            }).encode())
            
            response = json.loads(self.sock.recv(4096).decode())
            
            if response['status'] != 'ok':
                messagebox.showerror("Error", response.get('message', 'Failed to get puzzle details'))
                return
            
            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create main frame with white background
            main_frame = tk.Frame(self.root, bg='white')
            main_frame.pack(expand=True, fill="both", padx=40, pady=40)
            
            # Create grid and clues frame
            game_frame = tk.Frame(main_frame, bg='white')
            game_frame.pack(expand=True, fill="both")
            
            # Create grid frame with white background
            grid_frame = tk.Frame(game_frame, bg='white')
            grid_frame.pack(side="left", padx=20)
            
            # Parse grid
            grid_data = json.loads(response['grid'])
            
            self.cells = []
            for i, row in enumerate(grid_data):
                cell_row = []
                for j, char in enumerate(row):
                    cell = tk.Entry(
                        grid_frame,
                        width=2,
                        justify="center",
                        font=("Helvetica", 20),
                        bg='white',
                        fg='black'
                    )
                    cell.grid(row=i, column=j, padx=2, pady=2)
                    if char != '_':
                        cell.insert(0, char)
                        cell.configure(state="readonly")
                    cell_row.append(cell)
                self.cells.append(cell_row)
            
            # Force grid frame to update
            grid_frame.update_idletasks()
            
            # Create clues frame
            clues_frame = tk.Frame(game_frame, bg='white')
            clues_frame.pack(side="right", padx=20, fill="both", expand=True)
            
            # Parse and display clues
            clues_data = json.loads(response['clues'])
            
            # Display across clues
            tk.Label(
                clues_frame,
                text="Across:",
                font=("Helvetica", 14, "bold"),
                bg='white',
                fg='black'
            ).pack(anchor="w", pady=(0, 5))
            
            for clue in clues_data['across']:
                tk.Label(
                    clues_frame,
                    text=clue,
                    font=("Helvetica", 12),
                    bg='white',
                    fg='black',
                    wraplength=300,
                    justify="left"
                ).pack(anchor="w", pady=2)
            
            # Display down clues
            tk.Label(
                clues_frame,
                text="Down:",
                font=("Helvetica", 14, "bold"),
                bg='white',
                fg='black'
            ).pack(anchor="w", pady=(15, 5))
            
            for clue in clues_data['down']:
                tk.Label(
                    clues_frame,
                    text=clue,
                    font=("Helvetica", 12),
                    bg='white',
                    fg='black',
                    wraplength=300,
                    justify="left"
                ).pack(anchor="w", pady=2)
            
            # Create button frame
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(pady=20)
            
            tk.Button(
                button_frame,
                text="Submit Answer",
                command=lambda: self.submit_solution(puzzle_id),
                font=("Helvetica", 12),
                bg='#2196F3',
                fg='black'
            ).pack(side="left", padx=5)
            
            tk.Button(
                button_frame,
                text="Back to List",
                command=self.show_puzzle_list,
                font=("Helvetica", 12),
                bg='#2196F3',
                fg='black'
            ).pack(side="left", padx=5)
            
            # Force the entire window to update
            self.root.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

        self.timer_label = tk.Label(button_frame, text="Time: 0s", font=("Helvetica", 12), bg='white', fg='black')
        self.timer_label.pack(side="left", padx=10)
        self.update_timer()

    def update_timer(self):
        if hasattr(self, 'start_time'):
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
            self.root.after(1000, self.update_timer)
    
    def submit_solution(self, puzzle_id):
        """Submit answer"""

        elapsed_time = int(time.time() - self.start_time)

        try:
            # Collect answer
            solution = []
            for row in self.cells:
                solution_row = []
                for cell in row:
                    value = cell.get().strip().upper()
                    if not value and cell['state'] != 'readonly':
                        messagebox.showerror("Error", "Please fill in all blanks")
                        return
                    solution_row.append(value)
                solution.append(solution_row)
            
            self.sock.send(json.dumps({
                'action': 'submit_solution',
                'username': self.current_user,
                'puzzle_id': puzzle_id,
                'solution': json.dumps(solution),
                'time_taken': elapsed_time
            }).encode())
            
            response = json.loads(self.sock.recv(4096).decode())
            
            if response['status'] == 'ok':
                messagebox.showinfo("Success", "Correct answer!")
                self.show_puzzle_list()
            else:
                messagebox.showerror("Error", response.get('message', 'Incorrect answer, please try again'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
    
    def show_add_puzzle(self):
        """Display add puzzle interface"""
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
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='black'
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
        
        # Add instructions
        instruction_text = """Puzzle Creation Guide:
1. Use underscore '_' to mark letters that players need to guess
2. Other characters will be shown as hints
3. Don't add spaces between characters in each row
4. Each puzzle must have at least one letter to guess

Example:
Grid:       Answer:
C_T        CAT
(Shows 'C' and 'T', player needs to guess 'A')"""
        
        instruction_label = tk.Label(
            scrollable_frame,
            text=instruction_text,
            font=("Helvetica", 12),
            bg='white',
            fg='black',
            justify=tk.LEFT
        )
        instruction_label.pack(pady=10, anchor='w')
        
        # Title input
        title_frame = tk.Frame(scrollable_frame, bg='white')
        title_frame.pack(fill="x", pady=5)
        
        tk.Label(title_frame, text="Title:", font=("Helvetica", 12), bg='white', fg='black').pack(side="left", padx=5)
        title_entry = tk.Entry(title_frame, font=("Helvetica", 12), width=30, bg='white', fg='black')
        title_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        # Grid input
        tk.Label(scrollable_frame, text="Grid (with underscores):", font=("Helvetica", 12), bg='white', fg='black').pack(anchor="w", pady=5)
        grid_text = tk.Text(scrollable_frame, height=5, width=30, font=("Helvetica", 12), bg='white', fg='black')
        grid_text.pack(pady=5)
        
        # Answer input
        tk.Label(scrollable_frame, text="Complete Answer:", font=("Helvetica", 12), bg='white', fg='black').pack(anchor="w", pady=5)
        answer_text = tk.Text(scrollable_frame, height=5, width=30, font=("Helvetica", 12), bg='white', fg='black')
        answer_text.pack(pady=5)
        
        # Clues input
        tk.Label(scrollable_frame, text="Clues:", font=("Helvetica", 12), bg='white', fg='black').pack(anchor="w", pady=5)
        clues_text = tk.Text(scrollable_frame, height=10, width=30, font=("Helvetica", 12), bg='white', fg='black')
        clues_text.pack(pady=5)
        
        def validate_and_submit():
            """Validate input and submit puzzle"""
            title = title_entry.get().strip()
            grid = grid_text.get("1.0", "end-1c").strip()
            answer = answer_text.get("1.0", "end-1c").strip()
            clues = clues_text.get("1.0", "end-1c").strip()
            
            # Validate title
            if not title:
                messagebox.showerror("Error", "Please enter a title")
                return
            
            # Validate grid
            if not grid:
                messagebox.showerror("Error", "Please enter the grid")
                return
            
            # Validate if there's at least one letter to guess
            if '_' not in grid:
                messagebox.showerror("Error", "Grid must contain at least one underscore '_' for letters to guess")
                return
            
            # Validate answer
            if not answer:
                messagebox.showerror("Error", "Please enter the complete answer")
                return
            
            # Validate answer matches grid
            grid_chars = [c for c in grid if c != '_']
            for c in grid_chars:
                if c not in answer:
                    messagebox.showerror("Error", f"Answer is missing the hint character '{c}'")
                    return
            
            if len(answer.replace('\n', '')) != len(grid.replace('\n', '')):
                messagebox.showerror("Error", "Answer length doesn't match grid")
                return
            
            # Validate clues
            if not clues:
                messagebox.showerror("Error", "Please enter clues")
                return
            
            try:
                self.sock.send(json.dumps({
                    'action': 'add_puzzle',
                    'title': title,
                    'author': self.current_user,
                    'grid': grid,
                    'answer': answer,
                    'clues': clues
                }).encode())
                
                response = json.loads(self.sock.recv(4096).decode())
                
                if response['status'] == 'ok':
                    messagebox.showinfo("Success", "Puzzle added successfully!")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Error", response.get('message', 'Failed to add puzzle'))
                    
            except Exception as e:
                messagebox.showerror("Error", f"Network error: {str(e)}")
        
        # Submit button
        tk.Button(
            scrollable_frame,
            text="Submit",
            command=validate_and_submit,
            font=("Helvetica", 12),
            bg='#2196F3',
            fg='black'
        ).pack(pady=20)
    
    def show_statistics(self):
        """Display statistics"""
        try:
            self.sock.send(json.dumps({
                'action': 'get_statistics',
                'username': self.current_user
            }).encode())
            
            response = json.loads(self.sock.recv(4096).decode())
            
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
                font=("Helvetica", 12),
                bg='#2196F3',
                fg='black'
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")

if __name__ == "__main__":
    CrosswordClient()
