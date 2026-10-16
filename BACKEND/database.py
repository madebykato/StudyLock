import sqlite3

class Database:
    def __init__(self, db_name="studylock.db"):
        self.db_name = db_name

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn