import sqlite3
from datetime import datetime

DB_NAME = "patients.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table with role
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'nurse'
    )
    """)

    # Patient history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        age INTEGER,
        blood_pressure REAL,
        glucose REAL,
        risk_level TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_user(username, password, role="nurse"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_role(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None

def add_patient_record(username, age, bp, glucose, risk):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO history (username, age, blood_pressure, glucose, risk_level, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, age, bp, glucose, risk, date))
    conn.commit()
    conn.close()

def get_patient_history(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT age, blood_pressure, glucose, risk_level, date 
        FROM history WHERE username=?
        ORDER BY date ASC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, age, blood_pressure, glucose, risk_level, date 
        FROM history ORDER BY date ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
