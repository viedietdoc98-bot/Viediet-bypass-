# database.py
import sqlite3
import json
from datetime import datetime
from config import DB_FILE

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TEXT,
                referred_by INTEGER,
                balance INTEGER DEFAULT 0,
                total_uses INTEGER DEFAULT 0,
                last_use TEXT
            );
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                timestamp TEXT,
                reward_given INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                offer_name TEXT,
                platform TEXT,
                status TEXT,
                details TEXT,
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        # Insert default config if not exists
        conn.execute('''
            INSERT OR IGNORE INTO config (key, value)
            VALUES ('api_config', ?)
        ''', (json.dumps({}),))
        conn.commit()

def get_user(user_id):
    with get_db() as conn:
        cur = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cur.fetchone()

def create_user(user_id, username, first_name, last_name, referred_by=None):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, registered_at, referred_by, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.utcnow().isoformat(), referred_by, 0))
        conn.commit()

def update_user_balance(user_id, delta):
    with get_db() as conn:
        conn.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (delta, user_id))
        conn.commit()

def log_usage(user_id, offer_name, platform, status, details=''):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO usage_logs (user_id, offer_name, platform, status, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, offer_name, platform, status, details, datetime.utcnow().isoformat()))
        conn.commit()
        conn.execute('UPDATE users SET total_uses = total_uses + 1, last_use = ? WHERE user_id = ?',
                     (datetime.utcnow().isoformat(), user_id))
        conn.commit()

def add_referral(referrer_id, referred_id, reward):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO referrals (referrer_id, referred_id, timestamp, reward_given)
            VALUES (?, ?, ?, ?)
        ''', (referrer_id, referred_id, datetime.utcnow().isoformat(), reward))
        conn.commit()

def get_referral_count(user_id):
    with get_db() as conn:
        cur = conn.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ?', (user_id,))
        return cur.fetchone()[0]

def get_api_config():
    with get_db() as conn:
        cur = conn.execute('SELECT value FROM config WHERE key = "api_config"')
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return {}

def set_api_config(config_dict):
    with get_db() as conn:
        conn.execute('REPLACE INTO config (key, value) VALUES ("api_config", ?)', (json.dumps(config_dict),))
        conn.commit()
