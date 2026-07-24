import sqlite3

conn = sqlite3.connect("exam.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER,

    exam_id INTEGER,

    score INTEGER,

    total_questions INTEGER,

    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()

conn.close()

print("✅ Results Table Created Successfully")