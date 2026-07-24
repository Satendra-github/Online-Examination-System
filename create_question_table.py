import sqlite3

conn = sqlite3.connect("exam.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(

id INTEGER PRIMARY KEY AUTOINCREMENT,

subject TEXT,

topic TEXT,

difficulty TEXT,

question_type TEXT,

question TEXT,

option1 TEXT,

option2 TEXT,

option3 TEXT,

option4 TEXT,

answer TEXT

)
""")

conn.commit()

conn.close()

print("✅ Question Bank Table Created Successfully")