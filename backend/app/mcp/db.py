import sqlite3
import os

# Put the database in the root of the backend folder
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "crm.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create a table for property tours
    c.execute('''CREATE TABLE IF NOT EXISTS tours
                 (property_id TEXT PRIMARY KEY, available_dates TEXT, agent_name TEXT)''')

    # Insert dummy data that maps to the properties from Day 3
    c.execute("INSERT OR REPLACE INTO tours VALUES ('1', 'Saturday 10 AM, Sunday 2 PM', 'Sarah')")
    c.execute("INSERT OR REPLACE INTO tours VALUES ('2', 'Friday 4 PM, Monday 9 AM', 'Mike')")
    c.execute("INSERT OR REPLACE INTO tours VALUES ('3', 'Contact for appointment', 'David')")

    conn.commit()
    conn.close()
    print(f"SQLite DB Initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()