import sqlite3
from .init_db import initialize_database

def get_db_connection():
    """Get a connection to the SQLite database.
    Used by the server to access the database.
    """
    # Connect to the database
    conn = sqlite3.connect('database/crossword.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables and sample data.
    This function is called by the server at startup.
    """
    initialize_database()

# Import the DatabaseManager class for extended database operations
from .manager_db import DatabaseManager