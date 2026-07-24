import sqlite3

conn = sqlite3.connect("exam.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# Default Teacher
cursor.execute("""
INSERT OR IGNORE INTO teachers(name,email,password)
VALUES(?,?,?)
""", (
    "Nidhi",
    "nidhi@gmail.com",
    "123456"
))
conn.commit()
conn.close()

print("Database Created Successfully!")