from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from student_result import show_results
from utils import get_teacher_dashboard_stats
import os
import json
import sqlite3
from student_exam import show_exam
from utils import get_exam_questions, save_result, get_student_results
import base64

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
st.set_page_config(

    page_title="AI Exam Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------- Background Function ----------

import base64

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_bg(image_name):

    bg = get_base64(f"assests/{image_name}")

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        .main {{
            background: transparent !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0) !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "generated_exam" not in st.session_state:
    st.session_state.generated_exam = None

if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []

if "final_exam" not in st.session_state:
    st.session_state.final_exam = None

if "editing_question" not in st.session_state:
    st.session_state.editing_question = None

if "editing_db_question" not in st.session_state:
    st.session_state.editing_db_question = None

if "view_exam" not in st.session_state:
    st.session_state.view_exam = None

if "current_exam" not in st.session_state:
    st.session_state.current_exam = None

if "current_questions" not in st.session_state:
    st.session_state.current_questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "student_answers" not in st.session_state:
    st.session_state.student_answers = {}

if "student_page" not in st.session_state:
    st.session_state.student_page = "dashboard"

if "exam_started" not in st.session_state:
    st.session_state.exam_started = False

if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

def login_teacher(email, password):

    conn = sqlite3.connect("exam.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM teachers WHERE email=? AND password=?",
        (email, password)
    )

    teacher = cursor.fetchone()

    conn.close()

    return teacher

def login_student(email, password):

    conn = sqlite3.connect("exam.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE email=? AND password=?
        """,
        (email, password)
    )

    student = cursor.fetchone()

    conn.close()

    return student

def save_question(
    subject,
    topic,
    difficulty,
    question_type,
    question,
    options,
    answer
):

    conn = sqlite3.connect("exam.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM questions WHERE question=?",
        (question,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return False
    cursor.execute(
        """
        INSERT INTO questions
        (
        subject,
        topic,
        difficulty,
        question_type,
        question,
        option1,
        option2,
        option3,
        option4,
        answer
        )

        VALUES(?,?,?,?,?,?,?,?,?,?)
        """,

        (
            subject,
            topic,
            difficulty,
            question_type,
            question,
            options[0] if len(options)>0 else "",
            options[1] if len(options)>1 else "",
            options[2] if len(options)>2 else "",
            options[3] if len(options)>3 else "",
            answer
        )

    )

    conn.commit()
    conn.close()
    return True

def get_total_questions():
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def update_question(
    question_id,
    question,
    option1,
    option2,
    option3,
    option4,
    answer
):

    conn = sqlite3.connect("exam.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE questions
        SET
            question=?,
            option1=?,
            option2=?,
            option3=?,
            option4=?,
            answer=?
        WHERE id=?
        """,
        (
            question,
            option1,
            option2,
            option3,
            option4,
            answer,
            question_id
        )
    )

    conn.commit()
    conn.close()

def delete_question(question_id):
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM questions WHERE id=?",
        (question_id,)
    )
    conn.commit()
    conn.close()


def create_question_bank_pdf():
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            subject,
            topic,
            difficulty,
            question_type,
            question,
            option1,
            option2,
            option3,
            option4,
            answer
        FROM questions
    """)
    rows = cursor.fetchall()
    conn.close()
    pdf = SimpleDocTemplate("Question_Bank.pdf")
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("<b>AI Automated Exam Generator</b>", styles["Title"]))
    story.append(Paragraph("Question Bank", styles["Heading2"]))
    for i, row in enumerate(rows, start=1):
        story.append(Paragraph(f"<b>Question {i}</b>", styles["Heading2"]))
        story.append(Paragraph(f"Subject: {row[0]}", styles["BodyText"]))
        story.append(Paragraph(f"Topic: {row[1]}", styles["BodyText"]))
        story.append(Paragraph(f"Difficulty: {row[2]}", styles["BodyText"]))
        story.append(Paragraph(f"Type: {row[3]}", styles["BodyText"]))
        story.append(Paragraph(f"<b>{row[4]}</b>", styles["BodyText"]))
        story.append(Paragraph(f"A. {row[5]}", styles["BodyText"]))
        story.append(Paragraph(f"B. {row[6]}", styles["BodyText"]))
        story.append(Paragraph(f"C. {row[7]}", styles["BodyText"]))
        story.append(Paragraph(f"D. {row[8]}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Answer:</b> {row[9]}", styles["BodyText"]))
        story.append(Paragraph("<br/><br/>", styles["BodyText"]))
    pdf.build(story)
    return "Question_Bank.pdf"

def save_exam(exam_name, selected_questions):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    # Insert exam
    cursor.execute(
        "INSERT INTO exams (exam_name) VALUES (?)",
        (exam_name,)
    )

    exam_id = cursor.lastrowid

    # Link selected questions
    for question in selected_questions:

        question_id = question[0]

        cursor.execute(
            """
            INSERT INTO exam_questions
            (exam_id, question_id)
            VALUES (?,?)
            """,
            (exam_id, question_id)
        )

    conn.commit()
    conn.close()

def get_saved_exams():

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            exam_name,
            created_at
        FROM exams
        ORDER BY id DESC
    """)

    exams = cursor.fetchall()

    conn.close()

    return exams

def get_exam_question_count(exam_id):

    conn = sqlite3.connect("exam.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM exam_questions
        WHERE exam_id=?
        """,
        (exam_id,)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count



def delete_exam(exam_id):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    # Delete question mappings first
    cursor.execute(
        "DELETE FROM exam_questions WHERE exam_id=?",
        (exam_id,)
    )

    # Delete exam
    cursor.execute(
        "DELETE FROM exams WHERE id=?",
        (exam_id,)
    )

    conn.commit()
    conn.close()

def add_student(name, roll_no, email, password, branch, semester):

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (name, roll_no, email, password, branch, semester)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            roll_no,
            email,
            password,
            branch,
            semester
        ))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_students():

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            roll_no,
            email,
            branch,
            semester
        FROM students
        ORDER BY id DESC
    """)
    students = cursor.fetchall()
    conn.close()
    return students

def create_exam_pdf(exam_name, questions):

    pdf = SimpleDocTemplate(f"{exam_name}.pdf")

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(f"<b>{exam_name}</b>", styles["Title"])
    )

    story.append(
        Paragraph("<br/><br/>", styles["Normal"])
    )

    for i, q in enumerate(questions, start=1):

        story.append(
            Paragraph(f"<b>Q{i}. {q[4]}</b>", styles["Heading2"])
        )

        story.append(Paragraph(f"A. {q[5]}", styles["Normal"]))
        story.append(Paragraph(f"B. {q[6]}", styles["Normal"]))
        story.append(Paragraph(f"C. {q[7]}", styles["Normal"]))
        story.append(Paragraph(f"D. {q[8]}", styles["Normal"]))

        story.append(
            Paragraph(
                f"<font color='green'><b>Answer:</b> {q[9]}</font>",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph("<br/>", styles["Normal"])
        )

    pdf.build(story)

    return f"{exam_name}.pdf"
# ---------- Custom CSS ----------

st.markdown("""
<style>


h1{
    color:white;
    text-align:center;
    font-size:42px;
    margin-bottom:10px;
}

h2,h3{
    color:#f8fafc;
}

.stTextInput input{
    border-radius:10px;
    border:2px solid #3b82f6;
    padding:12px;
    background:#1e293b;
    color:white;
}

.stSelectbox div{
    border-radius:10px;
}

.stNumberInput input{
    border-radius:10px;
}

.stButton>button{
    width:100%;
    height:52px;
    border:none;
    border-radius:12px;
    background:linear-gradient(90deg,#2563eb,#06b6d4);
    color:white;
    font-size:18px;
    font-weight:bold;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.02);
    box-shadow:0px 8px 25px rgba(37,99,235,.4);
}

section[data-testid="stSidebar"]{
    background:#111827;
}

div[data-testid="metric-container"]{
    background:#1e293b;
    border-radius:15px;
    padding:20px;
    border:1px solid #334155;
}

.stAlert{
    border-radius:12px;
}
.block-container{
max-width:700px;
margin:auto;
padding-top:40px; 
}

</style>
""", unsafe_allow_html=True)

# ---------- Title ----------
if not st.session_state.logged_in:
    set_bg("login.jpg")

col1, col2, col3 = st.columns([1,2,1])

with col2:

    st.markdown("""
<div style="
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
">
    <h1 style="
        color:white;
        font-size:40px;
        font-weight:800;
        margin-top:20px;
        text-align:center;
        white-space:nowrap;
    ">
        🎓 AI-Powered Automated Exam Generator
    </h1>
</div>
""", unsafe_allow_html=True)
    
    st.markdown(
        "<h3 style='text-align:center;color:#9CCBFF;'>Assessment Platform</h3>",
        unsafe_allow_html=True
    )

    portal = st.radio(
        "Select Portal",
        ["Teacher", "Student"],
        horizontal=True
    )

   
    if portal == "Teacher":
        st.subheader("👨‍🏫 Teacher Login")
    else:
        st.subheader("🎓 Student Login")

    email = st.text_input(f"{portal} Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    login = st.button("Login", use_container_width=True)

    if login:
        if portal == "Teacher":
            teacher = login_teacher(email, password)
            if teacher:
                st.session_state.logged_in = True
                st.session_state.user_type = "teacher"
                st.success("Teacher Login Successful")
                st.rerun()
            else:
                st.error("Invalid Teacher Credentials")

        else:
            student = login_student(email, password)
            if student:
                st.session_state.logged_in = True
                st.session_state.user_type = "student"
                st.session_state.student = student
                st.success("Student Login Successful")
                st.rerun()
            else:
                st.error("Invalid Student Credentials")

# ================= Sidebar =================

if st.session_state.logged_in:

    if st.session_state.user_type == "teacher":

        st.sidebar.title("👨‍🏫 Teacher Panel")

        menu = st.sidebar.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📝 Generate Exam",
                "📚 Question Bank",
                "📂 Saved Exams",
                "👨‍🎓 Students",
                "📊 Analytics",
                "🚪 Logout"
            ]
        )

    else:

        st.sidebar.title("🎓 Student Panel")

        menu = st.sidebar.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📝 Available Exams",
                "📖 My Results",
                "🚪 Logout"
            ]
        )


else:
    st.stop()



# ---------------- Background ----------------

# 👇👇 YAHAN paste karna hai

if not st.session_state.logged_in:

    set_bg("login.jpg")

elif st.session_state.user_type=="teacher":

    if menu=="🏠 Dashboard":
        set_bg("dashboard.jpg")

    elif menu=="📝 Generate Exam":
        set_bg("generate.jpg")

    elif menu=="📚 Question Bank":
        set_bg("questionbank.jpg")

    elif menu=="👨‍🎓 Students":
        set_bg("student.jpg")

    elif menu=="📂 Saved Exams":
        set_bg("dashboard.jpg")      # ya agar alag image banana hai to savedexams.jpg bana lena

    elif menu=="📊 Analytics":
        set_bg("result.jpg")

else:

    if menu=="🏠 Dashboard":
        set_bg("dashboard.jpg")

    elif menu=="📝 Available Exams":
        set_bg("generate.jpg")

    elif menu=="📖 My Results":
        set_bg("result.jpg")

# ================= Dashboard =================

if menu == "🏠 Dashboard":

    if st.session_state.user_type == "teacher":
        st.title("📊 Teacher Dashboard")
        stats = get_teacher_dashboard_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👨‍🎓 Students", stats[0])
        with col2:
            st.metric("📝 Exams", stats[1])
        with col3:
            st.metric("❓ Questions", stats[2])
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("📋 Attempts", stats[3])
        with col5:
            st.metric(
                "📈 Average %",
                f"{stats[4]:.1f}%" if stats[4] else "0%"
            )

        with col6:
            st.metric(
                "🏆 Highest %",
                f"{stats[5]:.1f}%" if stats[5] else "0%"
            )

    else:

        student = st.session_state.student

        st.title("🎓 Student Dashboard")

        st.success(f"Welcome {student[1]} 👋")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("📝 Available Exams", len(get_saved_exams()))

        with col2:
            st.metric("🏆 Completed Exams", 0)

        st.divider()

        st.info("📝 Use the 'Available Exams' menu from the sidebar to start an exam.")

# ================= Generate Exam =================

elif menu == "📝 Generate Exam":

    st.title("📝 AI Exam Generator")

    subject = st.text_input("📚 Subject")

    topic = st.text_input("📝 Topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    num_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5
    )

    question_type = st.selectbox(
        "Question Type",
        [
            "MCQ",
            "True/False",
            "Short Answer"
        ]
    )

    generate = st.button("🚀 Generate Exam")

    if generate:

        st.session_state.generated_exam = None

        if subject.strip() == "":
            st.error("❌ Please enter Subject")
            st.stop()

        if topic.strip() == "":
            st.error("❌ Please enter Topic")
            st.stop()

        prompt = f"""
You are an expert exam paper generator.

Generate exactly {num_questions} {question_type} questions.

Subject: {subject}

Topic: {topic}

Difficulty: {difficulty}

Return ONLY valid JSON.

Format:

[
{{
    "question":"Question",
    "options":["A","B","C","D"],
    "answer":"Correct Answer"
}}
]
"""
        with st.spinner("🤖 Gemini is generating your exam..."):

            response = model.generate_content(prompt)

            exam_text = response.text

            # Remove markdown if Gemini returns it
            exam_text = exam_text.replace("```json", "")
            exam_text = exam_text.replace("```", "")
            exam_text = exam_text.strip()

            try:
                questions = json.loads(exam_text)

                st.session_state.generated_exam = {
                    "subject": subject,
                    "topic": topic,
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "questions": questions
                }

                st.success("✅ Exam Generated Successfully!")

            except Exception:

                st.error("❌ Invalid JSON received from Gemini.")

                st.code(exam_text)

# ================= Display Questions =================

    if st.session_state.generated_exam:

        exam = st.session_state.generated_exam

        for i, q in enumerate(exam["questions"], start=1):

            st.subheader(f"Question {i}")

            st.write(q["question"])

            # Show Options
            if "options" in q:
                for option in q["options"]:
                    st.write("•", option)

            # Show Answer
            with st.expander("✅ Show Answer"):
                st.success(q["answer"])

            # Teacher Action Buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("💾 Save", key=f"save_{i}"):

                    try:

                        saved = save_question(
                            exam["subject"],
                            exam["topic"],
                            exam["difficulty"],
                            exam["question_type"],
                            q["question"],
                            q.get("options", []),
                            q["answer"]
                        )

                        if saved:
                            st.success("✅ Saved Successfully!")
                            conn = sqlite3.connect("exam.db")
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM questions")
                            count = cursor.fetchone()[0]
                            conn.close()
                            st.info(f"📚 Total Questions in Database: {count}")
                            
                        else:
                            st.warning("⚠ This question is already in the Question Bank.")
                    except Exception as e:
                        st.error(e)

            with col2:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.editing_question = i - 1
                    st.rerun()

            with col3:
                if st.button("🔄 Regenerate", key=f"regen_{i}"):
                    prompt = f"""
            Generate ONLY ONE {exam["difficulty"]} {exam["question_type"]} question.
            Subject: {exam["subject"]}
            Topic: {exam["topic"]}
            Return JSON in this format:
            {{
                "question": "...",
                "options": ["A", "B", "C", "D"],
                "answer": "..."
            }}
            """

                    response = model.generate_content(prompt)

                    exam_text = response.text
                    exam_text = exam_text.replace("```json", "")
                    exam_text = exam_text.replace("```", "")
                    exam_text = exam_text.strip()

                    new_question = json.loads(exam_text)
                    exam["questions"][i - 1] = new_question
                    st.session_state.generated_exam = exam
                    st.success("✅ Question Regenerated!")
                    st.rerun()

            with col4:
                if st.button("🗑 Delete", key=f"delete_generated_{i}"):
                    exam["questions"].pop(i - 1)
                    st.session_state.generated_exam = exam
                    st.rerun()

            st.divider()

elif menu == "📚 Question Bank":

    if st.button("📄 Generate PDF"):
        pdf_file = create_question_bank_pdf()
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="⬇ Download Question Bank PDF",
                data=file,
                file_name="Question_Bank.pdf",
                mime="application/pdf"
            )

    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject, topic, difficulty,
            question_type, question,
            option1, option2, option3, option4,
            answer
        FROM questions
    """)

    rows = cursor.fetchall()

    conn.close()

    if len(rows) == 0:
        st.info("No questions saved yet.")

    else:
        for row in rows:
            selected = st.checkbox(
            "Select for Exam",
            key=f"select_{row[0]}"
            )
            if selected:
                if row not in st.session_state.selected_questions:
                    st.session_state.selected_questions.append(row)

            else:
                if row in st.session_state.selected_questions:
                    st.session_state.selected_questions.remove(row)

            st.subheader(f"Question ID: {row[0]}")

            st.write(f"**Subject:** {row[1]}")
            st.write(f"**Topic:** {row[2]}")
            st.write(f"**Difficulty:** {row[3]}")
            st.write(f"**Type:** {row[4]}")

            if st.session_state.editing_db_question == row[0]:

                edited_question = st.text_area(
                    "Question",
                    value=row[5],
                    key=f"q_{row[0]}"
                )

                option1 = st.text_input(
                    "Option A",
                    value=row[6],
                    key=f"o1_{row[0]}"
                )

                option2 = st.text_input(
                    "Option B",
                    value=row[7],
                    key=f"o2_{row[0]}"
                )

                option3 = st.text_input(
                    "Option C",
                    value=row[8],
                    key=f"o3_{row[0]}"
                )

                option4 = st.text_input(
                    "Option D",
                    value=row[9],
                    key=f"o4_{row[0]}"
                )

                answer = st.text_input(
                    "Answer",
                    value=row[10],
                    key=f"ans_{row[0]}"
                )

            else:

                st.write(f"**Question:** {row[5]}")

                st.write("A.", row[6])
                st.write("B.", row[7])
                st.write("C.", row[8])
                st.write("D.", row[9])

                st.success(f"Answer: {row[10]}")

            col1, col2, col3 = st.columns([1, 1, 5])

            with col1:
                if st.button(
                    "✏️ Edit",
                    key=f"edit_db_{row[0]}"
                ):
                    st.session_state.editing_db_question = row[0]
                    st.rerun()

            with col2:
                if st.button(
                    "🗑 Delete",
                    key=f"delete_db_{row[0]}"
                ):

                    delete_question(row[0])
                    st.success("✅ Question Deleted Successfully!")
                    st.rerun()
            st.divider()

        if st.button("📝 Create Exam"):
            st.session_state.final_exam = (
                st.session_state.selected_questions.copy()
            )
            st.success(
                f"{len(st.session_state.final_exam)} questions added to exam."
            )

        if st.session_state.final_exam:

            exam_name = st.text_input(
            "📝 Enter Exam Name"
            )
            st.divider()
            st.title("📝 Final Exam")
            for i, row in enumerate(st.session_state.final_exam, start=1):
                st.subheader(f"Question {i}")
                st.write(f"**Subject:** {row[1]}")
                st.write(f"**Topic:** {row[2]}")
                st.write(f"**Difficulty:** {row[3]}")
                st.write(f"**Type:** {row[4]}")

                st.write(f"**Question:** {row[5]}")

                st.write("A.", row[6])
                st.write("B.", row[7])
                st.write("C.", row[8])
                st.write("D.", row[9])

                with st.expander("✅ Answer"):
                    st.success(row[10])

                st.divider()
            if st.button("💾 Save Exam"):

                if exam_name.strip() == "":
                    st.warning("Please enter an exam name.")

                else:

                    save_exam(
                        exam_name,
                        st.session_state.final_exam
                    )

                    st.success("✅ Exam saved successfully!")


elif menu == "📂 Saved Exams":
    st.title("📂 Saved Exams")
    exams = get_saved_exams()
    if len(exams) == 0:
        st.info("No exams have been created yet.")
    else:
        for exam in exams:
            st.subheader(exam[1])
            st.write(f"Exam ID : {exam[0]}")
            st.write(f"Created : {exam[2]}")
            st.write(
                f"Questions : {get_exam_question_count(exam[0])}"
            )
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "👀 View",
                    key=f"view_{exam[0]}"
                ):
                    st.session_state.view_exam = exam[0]

            with col2:
                if st.button(
                    "🗑 Delete",
                    key=f"delete_exam_{exam[0]}"
                ):
                    delete_exam(exam[0])
                    if st.session_state.view_exam == exam[0]:
                        st.session_state.view_exam = None
                    st.success("✅ Exam deleted successfully!")
                    st.rerun()

            with col3:
                if st.button(
                    "📄 PDF",
                    key=f"pdf_{exam[0]}"
                ):
                    questions = get_exam_questions(exam[0])
                    filename = create_exam_pdf(
                        exam[1],
                        questions
                    )
                    with open(filename, "rb") as file:
                        st.download_button(
                            "⬇ Download PDF",
                            file,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"download_{exam[0]}"
                        )
            st.divider()

        if st.session_state.view_exam:

            st.divider()
            st.header("📝 Exam Preview")

            questions = get_exam_questions(st.session_state.view_exam)

            for i, q in enumerate(questions, start=1):

                st.markdown(f"### Q{i}. {q[4]}")

                st.write("A.", q[5])
                st.write("B.", q[6])
                st.write("C.", q[7])
                st.write("D.", q[8])

                with st.expander("Answer"):
                    st.success(q[9])

                st.divider()

elif menu == "👨‍🎓 Students":
    st.title("👨‍🎓 Student Management")
    st.subheader("➕ Add Student")
    name = st.text_input(
        "Student Name",
        key="student_name"
    )

    roll = st.text_input(
        "Roll Number",
        key="student_roll"
    )

    email = st.text_input(
        "Student Email",
        key="student_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="student_password"
    )

    branch = st.text_input(
        "Branch",
        key="student_branch"
    )

    semester = st.text_input(
        "Semester",
        key="student_semester"
    )
    if st.button("Add Student"):
        if name == "" or email == "" or password == "" or roll == "":
            st.warning("Please fill all required fields.")
        else:
            saved = add_student(
                name,
                roll,
                email,
                password,
                branch,
                semester
            )
            if saved:
                st.success("✅ Student Added Successfully")
                st.rerun()
            else:
                st.error("Student already exists.")
    st.divider()
    st.subheader("📋 Registered Students")
    students = get_students()
    if len(students) == 0:
        st.info("No students found.")
    else:
        for student in students:
            st.write(f"### {student[1]}")
            st.write(f"Roll No : {student[2]}")
            st.write(f"Email : {student[3]}")
            st.write(f"Branch : {student[4]}")
            st.write(f"Semester : {student[5]}")
            st.divider()

elif menu == "📝 Available Exams":

    if st.session_state.exam_started:
        show_exam()
        st.stop()

    if st.session_state.exam_submitted:

        if "score" in st.session_state and "total_questions" in st.session_state:

            st.success(
                f"🎉 Exam submitted successfully!\n\n"
                f"Your Score: {st.session_state.score}/{st.session_state.total_questions}"
            )

            st.balloons()

        else:
            st.error("Score could not be calculated.")

        st.session_state.exam_submitted = False

    st.title("📝 Available Exams")
    exams = get_saved_exams()
    if len(exams) == 0:
        st.info("No exams available.")
    else:
        for exam in exams:
            question_count = get_exam_question_count(exam[0])
            st.container(border=True)
            st.subheader(exam[1])
            st.write(f"📚 Questions : {question_count}")
            st.write(f"📅 Created : {exam[2]}")
            if st.button("🚀 Start Exam", key=f"exam_{exam[0]}"):

                questions = get_exam_questions(exam[0])

                st.session_state.current_exam = exam[0]
                st.session_state.current_questions = questions
                st.session_state.current_question = 0
                st.session_state.student_answers = {}
                st.session_state.exam_started = True
                st.rerun()
            st.divider()

elif menu == "📖 My Results":
    show_results()
