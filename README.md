# Crossword Puzzle Platform
An interactive online platform for creating, sharing, and solving crossword puzzles with social features and statistics tracking.

## Acknowledgements
- This is the groupwork for CS5003_P3 in University of St Andrews
- Thanks to our coursework supervisor: Dr Edwin Brady
- Thanks to all contributors to this projects in Group7, our team-members are
  - 240009696 
  - 240016954 
  - 240021230 
  - 240029820 
  - 240032527  
- (The upper ranking is in no particular order and is arranged according to student ID numbers.)
- Thanks to the creators of the referenced crossword platforms for inspiration.

---
 
## Overview
This application allows users to:
- Play crossword puzzles from a curated collection
- Create and share their own puzzles
- Track solving statistics and rankings
- Connect with friends and send messages
- Import puzzles from PUZ format

---
 
## Technical Stack
- **Frontend**: Python Tkinter for GUI
- **Backend**: Python socket server
- **Database**: SQLite for data persistence
- **Network**: Client-server architecture with JSON communication

---
 
## Installation
### Prerequisites
- Python 3.6 or higher
- Required Python packages:
  - tkinter (usually included with Python)
  - sqlite3 (usually included with Python)

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/crossword-platform.git
   cd crossword-platform
   ```
2. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies (if any additional are needed):
   ```
   pip install -r requirements.txt
   ```

---
 
## Getting Started

### Starting the Server
1. Initialize the database (first time only):
   ```
   python -m database.init_db
   ```
2. Start the server:
   ```
   python server.py
   ```
   The server will start listening on localhost:8888 by default.

### Starting the Client in a new terminal window
1. Launch the client application:
   ```
   python client.py
   ```
2. Login with your username and password (a new account will be automatically created if the username doesn't exist)
3. From the main menu, you can:
   - Browse and solve puzzles
   - View statistics
   - Create new puzzles
   - Access social features

---
 
## How to Play

1. **Solving Puzzles**:
   - Select a puzzle from the list
   - Click on a cell or use arrow keys to navigate
   - Type letters to fill in cells
   - Use the clues panel for guidance
   - Submit your solution when complete
2. **Creating Puzzles**:
   - Select "Add Puzzle" from the main menu
   - Set grid dimensions
   - Design your grid by marking black cells
   - Add across and down clues
   - Submit your creation to share with others
3. **Social Features**:
   - Add friends by username
   - Accept friend requests
   - Send messages to your friends
   - View your solving rankings

---
 
## Features
- **User Authentication**: Register and login system
- **Puzzle Library**: Browse and select from available puzzles
- **Interactive Solving Interface**: Visual grid with across/down clues
- **Puzzle Creation**: Create custom crossword puzzles
- **Statistics**: Track solving times and compare with other users
- **Social Features**: Add friends and exchange messages
- **Historical Rankings**: View your solving history and rankings
- **PUZ Import**: Import standard crossword puzzle files

---
 
## Inspiration
This project draws inspiration from these popular crossword platforms:
- [New York Times Crosswords](https://www.nytimes.com/crosswords)
- [Boatload Puzzles](https://www.boatloadpuzzles.com/playcrossword)
- [Best Crosswords](https://www.bestcrosswords.com/)

---
 
## Future Enhancements
- Automatic puzzle generation from word lists
- Challenge modes (timed mode, survival mode)
- Advanced puzzle editor with better visualization
- Mobile application support
