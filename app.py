import os
from datetime import date, datetime
from typing import Dict, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(page_title="StudentFlow AI", page_icon="🎓", layout="wide")


INDIA_STUDENT_CHALLENGES = [
    "Exam pressure and anxiety",
    "Time management with tuition/coaching",
    "Backlog and syllabus overload",
    "Language confidence (English/regional transitions)",
    "Unreliable internet/electricity",
    "Long commute and attendance pressure",
    "Family responsibilities and financial stress",
    "Career confusion and placement preparation",
]


@st.cache_resource
def get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def init_state() -> None:
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Namaste! I am your AI study mentor. Add your tasks and I will help you build a "
                    "realistic plan for students in India."
                ),
            }
        ]


def add_task(task: Dict) -> None:
    st.session_state.tasks.append(task)


def completion_rate(tasks: List[Dict]) -> float:
    if not tasks:
        return 0.0
    done = sum(1 for task in tasks if task["completed"])
    return round((done / len(tasks)) * 100, 1)


def risk_score(task: Dict) -> int:
    score = 0
    if task["priority"] == "High":
        score += 3
    elif task["priority"] == "Medium":
        score += 2
    else:
        score += 1

    days_left = (task["due_date"] - date.today()).days
    if days_left <= 1:
        score += 3
    elif days_left <= 3:
        score += 2
    else:
        score += 1

    if task["challenge"] in {
        "Exam pressure and anxiety",
        "Backlog and syllabus overload",
        "Family responsibilities and financial stress",
    }:
        score += 2

    return min(score, 10)


def build_ai_context() -> str:
    tasks = st.session_state.tasks
    if not tasks:
        return "No tasks yet."

    lines = []
    for idx, task in enumerate(tasks, start=1):
        lines.append(
            f"{idx}. {task['title']} | {task['subject']} | {task['priority']} | due {task['due_date']} | "
            f"challenge: {task['challenge']} | completed: {task['completed']}"
        )
    return "\n".join(lines)


def ask_ai(user_message: str) -> str:
    client = get_groq_client()
    if client is None:
        return (
            "⚠️ GROQ_API_KEY is not configured. Add it to your environment and restart the app. "
            "Example: export GROQ_API_KEY='your_key'"
        )

    system_prompt = (
        "You are an empathetic and practical student success mentor for Indian students (school, college, "
        "competitive exams). Give concise action plans with realistic low-cost steps. Focus on burnout "
        "prevention, exam strategy, language confidence, and time management. If user seems distressed, "
        "encourage talking to trusted people and professional support."
    )

    context = build_ai_context()
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Current task list:\n{context}\n\n"
                    f"Student question/request: {user_message}\n"
                    "Respond with: 1) key issue, 2) 7-day plan, 3) today focus (max 3 tasks), "
                    "4) one motivational line."
                ),
            },
        ],
        temperature=0.4,
        max_tokens=700,
    )
    return completion.choices[0].message.content


def task_dataframe() -> pd.DataFrame:
    if not st.session_state.tasks:
        return pd.DataFrame(
            columns=["Title", "Subject", "Priority", "Due Date", "Challenge", "Completed", "Risk"]
        )

    rows = []
    for task in st.session_state.tasks:
        rows.append(
            {
                "Title": task["title"],
                "Subject": task["subject"],
                "Priority": task["priority"],
                "Due Date": task["due_date"],
                "Challenge": task["challenge"],
                "Completed": task["completed"],
                "Risk": risk_score(task),
            }
        )
    return pd.DataFrame(rows)


def dashboard_tab() -> None:
    st.subheader("📊 Student Progress Dashboard")
    df = task_dataframe()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(df))
    col2.metric("Completion", f"{completion_rate(st.session_state.tasks)}%")
    avg_risk = round(df["Risk"].mean(), 1) if not df.empty else 0
    col3.metric("Average Stress Risk", avg_risk)

    if df.empty:
        st.info("Add tasks to see your dashboard insights.")
        return

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.groupby("Priority").size())
    st.bar_chart(df.groupby("Challenge").size())


def tasks_tab() -> None:
    st.subheader("✅ Plan Your Study Tasks")

    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        title = c1.text_input("Task title", placeholder="Revise Organic Chemistry chapter 3")
        subject = c2.text_input("Subject / Exam", placeholder="JEE Chemistry")

        c3, c4, c5 = st.columns(3)
        priority = c3.selectbox("Priority", ["High", "Medium", "Low"])
        due_date = c4.date_input("Due date", min_value=date.today())
        challenge = c5.selectbox("Primary challenge", INDIA_STUDENT_CHALLENGES)

        submitted = st.form_submit_button("Add task")
        if submitted:
            if not title.strip():
                st.warning("Please enter a task title.")
            else:
                add_task(
                    {
                        "id": int(datetime.now().timestamp() * 1000),
                        "title": title.strip(),
                        "subject": subject.strip() or "General",
                        "priority": priority,
                        "due_date": due_date,
                        "challenge": challenge,
                        "completed": False,
                    }
                )
                st.success("Task added successfully.")

    if not st.session_state.tasks:
        st.info("No tasks yet. Start by adding one above.")
        return

    st.markdown("### Your task list")
    for idx, task in enumerate(st.session_state.tasks):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(f"**{task['title']}**  \n{task['subject']} • Due: {task['due_date']}")
        c2.write(f"Priority: **{task['priority']}**")
        c3.write(f"Risk: **{risk_score(task)}/10**")
        task["completed"] = c4.checkbox("Done", value=task["completed"], key=f"done_{task['id']}_{idx}")


def ai_tab() -> None:
    st.subheader("🤖 AI Mentor (Groq)")
    st.caption("This assistant uses Groq API only.")

    with st.expander("Show current task context sent to AI"):
        st.code(build_ai_context())

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask for a plan: 'I have backlogs and exam anxiety, help me for 7 days'")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})


def resources_tab() -> None:
    st.subheader("🧭 Student Support Resources (India)")
    st.write(
        "If stress feels overwhelming, reach out early. Combining AI guidance with real human support is best."
    )
    st.markdown(
        """
- **KIRAN Mental Health Helpline:** 1800-599-0019  
- **Tele-MANAS:** 14416 or 1-800-891-4416  
- **Campus support:** Talk to class advisor/counsellor/mentor.  
- **Study strategy:** Use 50-10 focus cycles, daily 3-task limit, weekly review.  
        """
    )


init_state()

st.title("🎓 StudentFlow AI — Smart To-Do for Students in India")
st.write(
    "A Streamlit-first, open-source student planner that detects pressure points and generates practical plans using Groq."
)

if not os.getenv("GROQ_API_KEY"):
    st.warning("GROQ_API_KEY is missing. AI chat will be disabled until you set it.")


t1, t2, t3, t4 = st.tabs(["Dashboard", "Tasks", "AI Mentor", "Support"])
with t1:
    dashboard_tab()
with t2:
    tasks_tab()
with t3:
    ai_tab()
with t4:
    resources_tab()
