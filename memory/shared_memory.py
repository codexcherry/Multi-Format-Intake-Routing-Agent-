import sqlite3
import json
from datetime import datetime


class SharedMemory:
    def __init__(self, db_path="shared_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            type TEXT,
            timestamp TEXT,
            format TEXT,
            intent TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_id INTEGER,
            agent TEXT,
            data TEXT,
            thread_id TEXT,
            FOREIGN KEY (input_id) REFERENCES inputs (id)
        )
        ''')
        conn.commit()
        conn.close()

    def log_input(self, source, type, format, intent):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO inputs (source, type, timestamp, format, intent) VALUES (?, ?, ?, ?, ?)",
            (source, type, timestamp, format, intent)
        )
        # Get the ID of the last inserted row
        input_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return input_id

    def log_extracted_fields(self, input_id, agent, data, thread_id=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO extracted_fields (input_id, agent, data, thread_id) VALUES (?, ?, ?, ?)",
            (input_id, agent, json.dumps(data), thread_id)
        )
        conn.commit()
        conn.close()

    def get_input(self, input_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inputs WHERE id = ?", (input_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_input_timestamp(self, input_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM inputs WHERE id = ?", (input_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_extracted_fields(self, input_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM extracted_fields WHERE input_id = ?", (input_id,))
        results = cursor.fetchall()
        conn.close()
        return results 