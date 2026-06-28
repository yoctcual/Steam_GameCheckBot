import sqlite3

conn = sqlite3.connect("games.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT,
    release_date TEXT,
    price TEXT
)
""")

conn.commit()
conn.close()

print("games.dbを作り直しました")