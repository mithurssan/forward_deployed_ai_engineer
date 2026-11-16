import os
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.db_path = os.getenv("DATABASE_PATH", "complaints.db")
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory=sqlite3.Row
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()