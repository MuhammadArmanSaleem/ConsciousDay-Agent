import sqlite3
from datetime import datetime

def create_table():
    conn = sqlite3.connect("entries.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,  -- Store timestamp like "2025-06-19 14:32"
            journal TEXT,
            intention TEXT,
            dream TEXT,
            priorities TEXT,
            reflection TEXT,
            strategy TEXT
        )
    ''')
    conn.commit()
    conn.close()

def upgrade_table_if_needed():
    """Add 'username' column if missing in old DB schema."""
    conn = sqlite3.connect("entries.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(entries)")
    columns = [col[1] for col in c.fetchall()]

    if "username" not in columns:
        print("🔄 Adding missing 'username' column to entries table...")
        c.execute("ALTER TABLE entries ADD COLUMN username TEXT DEFAULT 'unknown'")
        conn.commit()

    conn.close()

def insert_entry(username, journal, intention, dream, priorities, reflection, strategy):
    conn = sqlite3.connect("entries.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('''
        INSERT INTO entries (username, timestamp, journal, intention, dream, priorities, reflection, strategy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, timestamp, journal, intention, dream, priorities, reflection, strategy))
    conn.commit()
    conn.close()

def get_all_entries(username):
    conn = sqlite3.connect("entries.db")
    c = conn.cursor()
    c.execute('SELECT * FROM entries WHERE username = ? ORDER BY id DESC', (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_entry(entry_id):
    conn = sqlite3.connect("entries.db")
    c = conn.cursor()
    c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
