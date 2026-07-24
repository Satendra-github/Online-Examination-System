import streamlit as st
from utils import get_student_results


def show_results():

    st.title("📖 My Results")

    results = get_student_results(st.session_state.student[0])

    if len(results) == 0:
        st.info("No exam results found.")

    else:

        for result in results:

            exam_name = result[0]
            score = result[1]
            total = result[2]
            date = result[3]

            percentage = round((score / total) * 100, 2)

            with st.container(border=True):

                st.subheader(exam_name)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Score", f"{score}/{total}")

                with col2:
                    st.metric("Percentage", f"{percentage}%")

                st.write(f"📅 {date}")

                if percentage >= 90:
                    st.success("🌟 Excellent performance! Keep it up.")
                elif percentage >= 75:
                    st.info("👍 Good work. A little more practice will make it even better.")
                elif percentage >= 50:
                    st.warning("📚 Fair attempt. Revise the important topics and practice more.")
                else:
                    st.error("💡 Needs improvement. Review the basics and attempt the exam again.")