import sqlite3
import os

DB_NAME = "oxcyshop.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table for users and currency
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    coins INTEGER DEFAULT 0,
                    xp INTEGER DEFAULT 0
                )''')
    
    # Table for persistent config/state (like leaderboard message ID)
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )''')
    
    # Table for GUIX listings (message_id -> price)
    c.execute('''CREATE TABLE IF NOT EXISTS guix_listings (
                    message_id INTEGER PRIMARY KEY,
                    price INTEGER
                )''')
    
    # Table for delivered UIs (user_id, link, password, claimed, delivered)
    c.execute('''CREATE TABLE IF NOT EXISTS ui_deliveries (
                    user_id INTEGER PRIMARY KEY,
                    link TEXT,
                    password TEXT,
                    claimed INTEGER DEFAULT 0,
                    delivered INTEGER DEFAULT 0
                )''')
    
    # Migrate existing tables if needed
    try:
        c.execute("ALTER TABLE ui_deliveries ADD COLUMN delivered INTEGER DEFAULT 0")
    except:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE ui_deliveries ADD COLUMN claimed INTEGER DEFAULT 0")
    except:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def add_guix_listing(message_id, price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO guix_listings (message_id, price) VALUES (?, ?)", (message_id, price))
    conn.commit()
    conn.close()

def get_guix_price(message_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT price FROM guix_listings WHERE message_id = ?", (message_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_coins(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_coins(user_id):
    user = get_user(user_id)
    return user[1] if user else 0

def remove_coins(user_id, amount):
    current = get_coins(user_id)
    if current >= amount:
        add_coins(user_id, -amount)
        return True
    return False

def get_top_users(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def set_config(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_config(key):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_ui_delivery(user_id, link, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO ui_deliveries (user_id, link, password) VALUES (?, ?, ?)", (user_id, link, password))
    conn.commit()
    conn.close()

def get_ui_delivery(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT link, password, claimed FROM ui_deliveries WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row if row else None

def mark_ui_claimed(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE ui_deliveries SET claimed = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def mark_ui_delivered(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE ui_deliveries SET delivered = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
