import sqlite3

def get_exam_questions(exam_id):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            q.subject,
            q.topic,
            q.difficulty,
            q.question_type,
            q.question,
            q.option1,
            q.option2,
            q.option3,
            q.option4,
            q.answer
        FROM questions q
        JOIN exam_questions eq
        ON q.id = eq.question_id
        WHERE eq.exam_id = ?
    """, (exam_id,))

    questions = cursor.fetchall()

    conn.close()

    return questions

def save_result(student_id, exam_id, score, total_questions):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results
        (student_id, exam_id, score, total_questions)
        VALUES (?, ?, ?, ?)
    """, (student_id, exam_id, score, total_questions))

    conn.commit()
    conn.close()

def get_student_results(student_id):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        exams.exam_name,
        results.score,
        results.total_questions,
        results.submitted_at
    FROM results
    JOIN exams
        ON exams.id = results.exam_id
    WHERE results.student_id = ?
    ORDER BY results.submitted_at DESC
""", (student_id,))

    results = cursor.fetchall()

    conn.close()

    return results

def get_teacher_dashboard_stats():

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Exams
    cursor.execute("SELECT COUNT(*) FROM exams")
    total_exams = cursor.fetchone()[0]

    # Total Questions
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    # Total Attempts
    cursor.execute("SELECT COUNT(*) FROM results")
    total_attempts = cursor.fetchone()[0]

    # Average Percentage
    cursor.execute("""
        SELECT AVG(score * 100.0 / total_questions)
        FROM results
    """)
    avg_percentage = cursor.fetchone()[0]

    # Highest Percentage
    cursor.execute("""
        SELECT MAX(score * 100.0 / total_questions)
        FROM results
    """)
    highest_percentage = cursor.fetchone()[0]

    conn.close()

    return (
        total_students,
        total_exams,
        total_questions,
        total_attempts,
        avg_percentage,
        highest_percentage
    )