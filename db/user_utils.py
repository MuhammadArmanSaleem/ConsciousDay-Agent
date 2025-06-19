# db/user_utils.py
import sqlite3

def create_users_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, name, email, password_hash):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, name, email, password_hash) VALUES (?, ?, ?, ?)",
        (username, name, email, password_hash)
    )
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user
