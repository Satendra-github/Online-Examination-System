import sqlite3

conn = sqlite3.connect("exam.db")
cursor = conn.cursor()

# ==========================
# Exam Information
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS exams(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================
# Questions inside an Exam
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS exam_questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    question_id INTEGER,
    FOREIGN KEY(exam_id) REFERENCES exams(id),
    FOREIGN KEY(question_id) REFERENCES questions(id)
)
""")

# ==========================
# Student Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    branch TEXT,
    semester TEXT
)
""")

# Save all changes
conn.commit()

# Close database
conn.close()

print("All tables created successfully!")