import os
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="AI Quiz Generator", page_icon="📝", layout="centered")

st.title("AI Quiz Generator")
st.caption("FastAPI + LangChain + Groq + PostgreSQL + Pydantic")

mode = st.sidebar.radio("Choose", ["Create Quiz", "Take Quiz"])

if mode == "Create Quiz":
    st.header("Create a quiz")
    title = st.text_input("Quiz title", "Python Basics Quiz")
    topic = st.text_input("Topic", "Python fundamentals")
    count = st.slider("Number of questions", 1, 20, 10)

    if st.button("Generate Quiz", type="primary"):
        with st.spinner("Generating and validating quiz..."):
            try:
                r = requests.post(
                    f"{API_URL}/quizzes",
                    json={
                        "title": title,
                        "topic": topic,
                        "number_of_questions": count,
                    },
                    timeout=120,
                )
                if r.ok:
                    public_id = r.json()["public_id"]
                    st.success("Quiz created successfully.")
                    st.code(f"https://quiz-frontend-5j5z.onrender.com/?quiz={public_id}")
                    st.info(f"Quiz ID: {public_id}")
                    st.write("For deployment, share your deployed frontend URL with ?quiz=" + public_id)
                    st.error(r.text)
            except requests.RequestException as e:
                st.error(f"Backend connection failed: {e}")

else:
    st.header("Take Quiz")
    query_id = st.query_params.get("quiz", "")
    public_id = st.text_input("Quiz ID or use ?quiz=...", query_id)

    if public_id:
        try:
            r = requests.get(f"{API_URL}/quizzes/{public_id}", timeout=30)
            if not r.ok:
                st.error(r.text)
            else:
                quiz = r.json()
                st.subheader(quiz["title"])
                st.write(f"Topic: {quiz['topic']}")
                name = st.text_input("Your name")

                answers = {}
                for i, q in enumerate(quiz["questions"], 1):
                    answers[q["id"]] = st.radio(
                        f"{i}. {q['question']}",
                        list(q["options"].keys()),
                        format_func=lambda key, opts=q["options"]: f"{key}. {opts[key]}",
                        key=f"q_{q['id']}"
                    )

                if st.button("Submit Quiz", type="primary"):
                    if not name.strip():
                        st.warning("Enter your name first.")
                    else:
                        payload = {
                            "student_name": name.strip(),
                            "answers": [
                                {"question_id": qid, "selected_answer": answer}
                                for qid, answer in answers.items()
                            ]
                        }
                        result = requests.post(
                            f"{API_URL}/quizzes/{public_id}/submit",
                            json=payload,
                            timeout=30
                        )
                        if result.ok:
                            data = result.json()
                            st.success(
                                f"Score: {data['score']} / {data['total_questions']} "
                                f"({data['percentage']}%)"
                            )
                        else:
                            st.error(result.text)
        except requests.RequestException as e:
            st.error(f"Backend connection failed: {e}")
