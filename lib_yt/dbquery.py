import sqlite3

conn = sqlite3.connect("videos.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM videos")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
