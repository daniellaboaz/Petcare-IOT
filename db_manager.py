import sqlite3
from threading import Lock

class DatabaseManager:
    def __init__(self, db_name="iot_monitor_petcare.db"):
        self.conn = sqlite3.connect(db_name, timeout=10)
        self.lock = Lock()  # Create a lock for thread safety
        self.create_tables()
        self.initialize_resources()

    def create_tables(self):
        with self.lock:  # Lock during database operations
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS resources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        resource_type TEXT NOT NULL,
                        quantity INTEGER NOT NULL
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS mqtt_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS levels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level_type TEXT NOT NULL,
                        current_level INTEGER NOT NULL
                    )
                """)

    def initialize_resources(self):
        resources = [("food", 40), ("water", 40), ("toys", 40), ("snacks", 40)]
        for resource in resources:
            if not self.get_resource(resource[0]):
                self.add_resource(resource[0], resource[1])

        # Set initial levels for food and water
        levels = [("food", 38), ("water", 38)]
        for level in levels:
            if not self.get_level(level[0]):
                self.add_level(level[0], level[1])

    def add_level(self, level_type, current_level):
        with self.lock:
            with self.conn:
                self.conn.execute("INSERT INTO levels (level_type, current_level) VALUES (?, ?)", (level_type, current_level))

    def get_level(self, level_type):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT current_level FROM levels WHERE level_type = ?", (level_type,))
            return cur.fetchone()

    def update_level(self, level_type, current_level):
        with self.lock:
            with self.conn:
                self.conn.execute("UPDATE levels SET current_level = ? WHERE level_type = ?", (current_level, level_type))

    def add_resource(self, resource_type, quantity):
        with self.lock:
            with self.conn:
                self.conn.execute("INSERT INTO resources (resource_type, quantity) VALUES (?, ?)", (resource_type, quantity))

    def update_resource(self, resource_type, quantity):
        with self.lock:
            with self.conn:
                self.conn.execute("UPDATE resources SET quantity = ? WHERE resource_type = ?", (quantity, resource_type))

    def get_resource(self, resource_type):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT quantity FROM resources WHERE resource_type = ?", (resource_type,))
            return cur.fetchone()

    def log_message(self, topic, message):
        with self.lock:
            with self.conn:
                self.conn.execute("INSERT INTO mqtt_logs (topic, message) VALUES (?, ?)", (topic, message))

    def close(self):
        with self.lock:
            self.conn.close()