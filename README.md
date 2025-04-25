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
  - puzpy (install via `pip install puzpy` for .PUZ file import support)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CS5003-P3-Crosswords.git
   cd CS5003-P3-Crosswords
   ```
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

---

## Getting Started

### Starting the Server

1. Initialize the database (first time only):

   ```bash
   python -m database.init_db
   ```

2. Start the server:

   ```bash
   python server.py
   ```

### Starting the Client

1. In a new terminal window (or tab), launch the client application:

   ```bash
   python client.py
   ```

2. Log in with your username and password. New accounts are automatically created on first login.

---

## How to Play

1. **Solving Puzzles**:
   - Select a puzzle from the list.
   - Click on a cell or use arrow keys to navigate.
   - Enter letters to fill in cells.
   - Use the clues panel for guidance.
   - Submit your solution when complete.

2. **Creating Puzzles**:
   - Select "Add New Puzzle" from the main menu.
   - Set grid dimensions.
   - Design your grid by marking black cells.
   - Add across and down clues.
   - Submit your creation to share with others.

3. **Social Features**:
   - Add friends by username.
   - Accept or reject friend requests.
   - Send messages to friends.
   - View your solving history and rankings.

---

## Inspiration
This project draws inspiration from these popular crossword platforms:
- [New York Times Crosswords](https://www.nytimes.com/crosswords)
- [Boatload Puzzles](https://www.boatloadpuzzles.com/playcrossword)
- [Best Crosswords](https://www.bestcrosswords.com/)

## Future Enhancements
- Automatic puzzle generation from word lists
- Challenge modes (timed mode, survival mode)
- Advanced puzzle editor with better visualization
- Mobile application support
