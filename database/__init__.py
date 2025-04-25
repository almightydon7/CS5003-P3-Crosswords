import sqlite3
import importlib

def get_db_connection():
    """Get a connection to the SQLite database.
    Used by the server to access the database.
    """
    # Connect to the database
    conn = sqlite3.connect('database/crossword.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database by running the init_db script."""
    # Dynamically reload to execute the module top-level code
    import database.init_db
    importlib.reload(database.init_db)

# Import the DatabaseManager class for extended database operations
from .manager_db import DatabaseManager
