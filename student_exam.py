import streamlit as st
from utils import save_result


def show_exam():

    st.title("📝 Student Exam")

    if len(st.session_state.current_questions) == 0:
        st.error("No questions loaded.")
        return

    questions = st.session_state.current_questions

    index = st.session_state.current_question

    # Safety check
    if index >= len(questions):
        st.session_state.current_question = 0
        index = 0

    q = questions[index]

    st.title("📝 Online Examination")

    st.progress((index + 1) / len(questions))

    st.markdown(f"## Question {index+1} of {len(questions)}")

    st.info(q[4])

    options = [
        q[5],
        q[6],
        q[7],
        q[8]
    ]

    previous_answer = st.session_state.student_answers.get(index, None)

    answer = st.radio(
        "Choose your answer",
        options,
        index=options.index(previous_answer) if previous_answer in options else None,
        key=f"question_{index}"
    )

    if answer:

        st.session_state.student_answers[index] = answer

    st.divider()

    col1, col2, col3 = st.columns([1,2,1])

    with col1:

        if index > 0:

            if st.button("⬅ Previous"):

                st.session_state.current_question -= 1

                st.rerun()

    with col2:

        st.write("")

    with col3:

        if index < len(questions) - 1:

            if st.button("Next ➡"):

                st.session_state.current_question += 1
                st.rerun()

        else:

            if st.button("✅ Submit Exam"):

                score = 0

                for i, question in enumerate(st.session_state.current_questions):

                    student_answer = st.session_state.student_answers.get(i)
                    correct_answer = question[9]

                    if student_answer == correct_answer:
                        score += 1

                total_questions = len(st.session_state.current_questions)

                st.session_state.score = score
                st.session_state.total_questions = total_questions
                save_result(
                    st.session_state.student[0],
                    st.session_state.current_exam,
                    score,
                    total_questions
                )


                st.session_state.exam_started = False
                st.session_state.exam_submitted = True

                st.rerun()