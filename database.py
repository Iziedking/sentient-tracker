import sqlite3

def init_db():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events 
                      (id TEXT PRIMARY KEY, platform TEXT, start_time TEXT, title TEXT, description TEXT, link TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (telegram_id TEXT PRIMARY KEY, google_calendar_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_metrics 
                      (telegram_id TEXT, platform TEXT, username TEXT, timestamp TEXT, 
                       engagement_rate REAL, message_count INTEGER, PRIMARY KEY(telegram_id, platform, username, timestamp))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS contributions 
                      (id TEXT PRIMARY KEY, repo TEXT, type TEXT, timestamp TEXT, author TEXT, url TEXT)''')
    conn.commit()
    return conn, cursor

def add_event(cursor, conn, event_id, platform, start_time, title, description, link):
    cursor.execute('INSERT OR IGNORE INTO events (id, platform, start_time, title, description, link) VALUES (?, ?, ?, ?, ?, ?)',
                   (event_id, platform, start_time, title or '', description or '', link))
    conn.commit()

def get_users(cursor):
    cursor.execute('SELECT telegram_id, google_calendar_id FROM users')
    return cursor.fetchall()

def add_user(cursor, conn, telegram_id, google_calendar_id=None):
    cursor.execute('INSERT OR REPLACE INTO users (telegram_id, google_calendar_id) VALUES (?, ?)',
                   (telegram_id, google_calendar_id))
    conn.commit()

def add_metric(cursor, conn, telegram_id, platform, username, timestamp, engagement_rate=0.0, message_count=0):
    cursor.execute('INSERT INTO user_metrics (telegram_id, platform, username, timestamp, engagement_rate, message_count) VALUES (?, ?, ?, ?, ?, ?)',
                   (telegram_id, platform, username, timestamp, engagement_rate, message_count))
    conn.commit()

def get_last_metric(cursor, telegram_id, platform, username):
    cursor.execute('SELECT engagement_rate, message_count FROM user_metrics WHERE telegram_id=? AND platform=? AND username=? ORDER BY timestamp DESC LIMIT 1',
                   (telegram_id, platform, username))
    return cursor.fetchone()

def add_contribution(cursor, conn, contrib_id, repo, contrib_type, timestamp, author, url):
    cursor.execute('INSERT OR IGNORE INTO contributions (id, repo, type, timestamp, author, url) VALUES (?, ?, ?, ?, ?, ?)',
                   (contrib_id, repo, contrib_type, timestamp, author, url))
    conn.commit()