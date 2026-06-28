import sqlite3

conn = sqlite3.connect("games.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE games
ADD COLUMN released_notified INTEGER DEFAULT 0
""")

conn.commit()
conn.close()

print("released_notified列追加完了")