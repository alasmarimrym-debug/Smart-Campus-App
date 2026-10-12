import html

from google import genai
import streamlit as st

from database import (
    add_flashcard,
    add_schedule,
    add_task,
    get_all_flashcards,
    get_all_schedules,
    get_all_tasks,
    init_db,
)

WEEK_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

st.set_page_config(
    page_title="Smart Campus Co-Pilot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_space_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(96, 165, 250, 0.18), transparent 28%),
                radial-gradient(circle at 88% 12%, rgba(167, 139, 250, 0.16), transparent 26%),
                radial-gradient(circle at 50% 100%, rgba(34, 211, 238, 0.10), transparent 38%),
                linear-gradient(180deg, #050816 0%, #0b1229 48%, #070b1a 100%);
            color: #e8f1ff;
            font-family: 'Outfit', sans-serif;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                radial-gradient(#ffffff 1px, transparent 1px),
                radial-gradient(#7dd3fc 1px, transparent 1px);
            background-size: 54px 54px, 92px 92px;
            background-position: 0 0, 28px 40px;
            opacity: 0.18;
            z-index: 0;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08101f 0%, #0d1630 100%);
            border-right: 1px solid rgba(125, 211, 252, 0.18);
        }
        [data-testid="stSidebar"] * { color: #dbeafe; }

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2.4rem;
            position: relative;
            z-index: 1;
        }

        h1, h2, h3, h4 { color: #f8fbff !important; letter-spacing: 0.02em; }

        .hero-title {
            text-align: center;
            font-size: 2.15rem;
            font-weight: 700;
            color: #f8fbff;
            margin: 0 0 0.35rem 0;
        }
        .hero-sub {
            text-align: center;
            color: #9ec5ff;
            margin-bottom: 1.6rem;
            font-size: 1.02rem;
        }

        div.stButton > button {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        div.stButton > button:hover {
            transform: translateY(-2px) scale(1.01);
        }

        .st-key-sched_btn button,
        .st-key-fc_btn button,
        .st-key-task_btn button,
        .st-key-ai_btn button {
            height: 160px !important;
            width: 100% !important;
            border-radius: 24px !important;
            font-size: 26px !important;
            box-shadow: 0 12px 28px rgba(2, 8, 32, 0.45) !important;
        }

        .st-key-sched_btn button {
            background: linear-gradient(160deg, #22d3ee 0%, #0284c7 100%) !important;
            color: #fff7cc !important;
            border: 1px solid rgba(186, 230, 253, 0.55) !important;
        }
        .st-key-fc_btn button {
            background: rgba(15, 23, 42, 0.72) !important;
            color: #fde68a !important;
            border: 5px solid #38bdf8 !important;
        }
        .st-key-task_btn button {
            background: rgba(15, 23, 42, 0.72) !important;
            color: #fde68a !important;
            border: 5px solid #fbbf24 !important;
        }
        .st-key-ai_btn button {
            background: linear-gradient(160deg, #1d4ed8 0%, #312e81 100%) !important;
            color: #fde68a !important;
            border: 1px solid rgba(196, 181, 253, 0.45) !important;
        }

        .st-key-back_home button {
            height: 44px !important;
            width: auto !important;
            min-width: 230px !important;
            padding: 0 1.35rem !important;
            border-radius: 999px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, #fbbf24, #f59e0b) !important;
            color: #0b1229 !important;
            border: none !important;
            box-shadow: 0 0 18px rgba(251, 191, 36, 0.35) !important;
        }

        .panel {
            background: rgba(12, 20, 42, 0.72);
            border: 1px solid rgba(125, 211, 252, 0.22);
            border-radius: 22px;
            padding: 1.2rem 1.3rem 1.4rem;
            box-shadow: 0 16px 40px rgba(2, 6, 23, 0.35);
            backdrop-filter: blur(10px);
        }

        [data-testid="stFormSubmitButton"] button {
            height: 44px !important;
            min-width: 160px !important;
            border-radius: 12px !important;
            font-size: 15px !important;
            background: linear-gradient(90deg, #22d3ee, #6366f1) !important;
            color: #f8fbff !important;
            border: none !important;
        }

        .week-wrap { overflow-x: auto; padding-bottom: 8px; }
        .week-board {
            display: grid;
            grid-template-columns: repeat(5, minmax(170px, 1fr));
            gap: 12px;
            margin-top: 0.4rem;
            min-width: 900px;
        }
        .day-col {
            background: rgba(8, 16, 36, 0.88);
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 16px;
            min-height: 280px;
            overflow: hidden;
        }
        .day-head {
            background: linear-gradient(90deg, #0ea5e9, #6366f1);
            color: #f8fafc;
            font-weight: 700;
            text-align: center;
            padding: 12px 8px;
            font-size: 0.95rem;
            letter-spacing: 0.04em;
        }
        .lecture {
            margin: 10px;
            padding: 12px;
            border-radius: 12px;
            background: linear-gradient(180deg, rgba(14, 165, 233, 0.18), rgba(99, 102, 241, 0.12));
            border: 1px solid rgba(125, 211, 252, 0.25);
        }
        .lecture-course {
            color: #f8fafc;
            font-weight: 700;
            font-size: 0.98rem;
            margin-bottom: 6px;
        }
        .lecture-time {
            color: #fde68a;
            font-size: 0.86rem;
        }
        .empty-slot {
            color: #7b93b8;
            text-align: center;
            padding: 28px 10px;
            font-size: 0.86rem;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 18px;
            overflow: hidden;
            border-radius: 14px;
        }
        .data-table th {
            background: #0ea5e9;
            color: #08101f;
            text-align: left;
            padding: 12px 14px;
            font-size: 0.92rem;
        }
        .data-table td {
            padding: 12px 14px;
            border-bottom: 1px solid rgba(125, 211, 252, 0.14);
            color: #e2e8f0;
            background: rgba(8, 16, 36, 0.55);
        }
        .data-table tr:hover td { background: rgba(14, 165, 233, 0.12); }

        .task-row, .card-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            border-radius: 14px;
            background: rgba(8, 16, 36, 0.7);
            border: 1px solid rgba(125, 211, 252, 0.18);
        }
        .badge {
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .badge-progress { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; }
        .badge-done { background: rgba(52, 211, 153, 0.2); color: #6ee7b7; }

        [data-testid="stChatMessage"] {
            background: rgba(8, 16, 36, 0.55);
            border: 1px solid rgba(125, 211, 252, 0.16);
            border-radius: 16px;
        }

        .stTextInput input, .stSelectbox [data-baseweb="select"] > div, .stTextArea textarea {
            background-color: rgba(8, 16, 36, 0.85) !important;
            color: #e8f1ff !important;
            border-radius: 12px !important;
        }

        @media (max-width: 700px) {
            .st-key-sched_btn button,
            .st-key-fc_btn button,
            .st-key-task_btn button,
            .st-key-ai_btn button { height: 120px !important; font-size: 20px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


def render_sidebar():
    st.sidebar.markdown("### 🪐 Smart Campus")
    st.sidebar.caption("Co-Pilot control deck")
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🔑 Gemini API Key")
    api_key = st.sidebar.text_input(
        "API Key",
        type="password",
        placeholder="Paste your Gemini API key",
        label_visibility="collapsed",
        key="gemini_api_key",
        help="Required only for the AI Assistant. Leave empty to browse the rest of the app.",
    )
    if api_key:
        st.sidebar.success("API key loaded")
    else:
        st.sidebar.info("Enter a key to enable the AI Assistant.")
    return api_key.strip() if api_key else ""


def render_back_button():
    if st.button("← Back to Home", key="back_home"):
        go_to("home")


def render_home():
    st.markdown('<p class="hero-title">🎓 Smart Campus Co-Pilot</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Navigate your campus tools from mission control</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("Class Schedule", use_container_width=True, key="sched_btn"):
            go_to("schedule")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Flashcard", use_container_width=True, key="fc_btn"):
            go_to("flashcard")
    with col2:
        if st.button("Task Management", use_container_width=True, key="task_btn"):
            go_to("tasks")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("AI Assistant", use_container_width=True, key="ai_btn"):
            go_to("ai")


def build_schedule_board(schedules):
    by_day = {day: [] for day in WEEK_DAYS}
    for row in schedules:
        day = row["day"]
        if day in by_day:
            by_day[day].append(row)

    board = ['<div class="week-wrap"><div class="week-board">']
    for day in WEEK_DAYS:
        board.append('<div class="day-col">')
        board.append(f'<div class="day-head">{html.escape(day)}</div>')
        lectures = by_day[day]
        if not lectures:
            board.append('<div class="empty-slot">No lectures</div>')
        else:
            for lecture in lectures:
                course = html.escape(lecture["course_name"])
                time_label = html.escape(lecture["time"])
                board.append(
                    f'<div class="lecture"><div class="lecture-course">{course}</div>'
                    f'<div class="lecture-time">⏰ {time_label}</div></div>'
                )
        board.append("</div>")
    board.append("</div></div>")

    table = [
        '<table class="data-table">',
        "<thead><tr><th>Day</th><th>Course</th><th>Time</th></tr></thead><tbody>",
    ]
    if schedules:
        for row in schedules:
            table.append(
                "<tr>"
                f"<td>{html.escape(row['day'])}</td>"
                f"<td>{html.escape(row['course_name'])}</td>"
                f"<td>{html.escape(row['time'])}</td>"
                "</tr>"
            )
    else:
        table.append('<tr><td colspan="3">No lectures saved yet.</td></tr>')
    table.append("</tbody></table>")
    return "".join(board) + "".join(table)


def render_schedule():
    st.markdown("<h1>📅 Class Schedule</h1>", unsafe_allow_html=True)
    st.caption("Weekly lecture board connected to student_app.db")

    with st.form("schedule_form", clear_on_submit=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            day = st.selectbox("Day", WEEK_DAYS)
        with col_b:
            course_name = st.text_input("Course Name")
        with col_c:
            time = st.text_input("Time (e.g., 08:00 AM - 10:00 AM)")
        submitted = st.form_submit_button("Add Lecture ➕")
        if submitted and course_name and time:
            add_schedule(day, course_name.strip(), time.strip())
            st.rerun()

    schedules = get_all_schedules()
    st.markdown(build_schedule_board(schedules), unsafe_allow_html=True)


def render_tasks():
    st.markdown("<h1>📝 Task Management</h1>", unsafe_allow_html=True)
    st.caption("Track campus work from the local database")

    with st.form("task_form", clear_on_submit=True):
        col_a, col_b = st.columns([2, 1])
        with col_a:
            task_title = st.text_input("Task Title")
        with col_b:
            task_status = st.selectbox("Status", ["In Progress", "Completed"])
        if st.form_submit_button("Add Task ➕") and task_title:
            add_task(task_title.strip(), task_status)
            st.rerun()

    tasks = get_all_tasks()
    if not tasks:
        st.info("No tasks yet. Add your first mission above.")
        return

    cards = []
    for task in tasks:
        badge_class = "badge-done" if task["status"] == "Completed" else "badge-progress"
        cards.append(
            '<div class="task-row">'
            f"<span>{html.escape(task['title'])}</span>"
            f'<span class="badge {badge_class}">{html.escape(task["status"])}</span>'
            "</div>"
        )
    st.markdown("".join(cards), unsafe_allow_html=True)


def render_flashcards():
    st.markdown("<h1>💡 Flashcards</h1>", unsafe_allow_html=True)
    st.caption("Study cards stored in the campus database")

    with st.expander("➕ Add New Flashcard"):
        with st.form("fc_form", clear_on_submit=True):
            subject = st.text_input("Subject")
            question = st.text_input("Question")
            answer = st.text_area("Answer")
            if st.form_submit_button("Save Card") and question and answer:
                add_flashcard((subject or "General").strip(), question.strip(), answer.strip())
                st.rerun()

    flashcards = get_all_flashcards()
    if not flashcards:
        st.info("No flashcards yet. Save a card to start revising.")
        return

    for card in flashcards:
        st.markdown(
            '<div class="card-row">'
            f"<strong>{html.escape(card['subject'])}</strong>"
            f"<span>{html.escape(card['question'])}</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        with st.expander("Show answer"):
            st.write(card["answer"])


def render_ai(api_key):
    st.markdown("<h1>🤖 AI Assistant</h1>", unsafe_allow_html=True)
    st.caption("Gemini 1.5 Flash — ask about courses, study plans, or campus tasks")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_panel = st.container()
    with chat_panel:
        if not st.session_state.messages:
            st.markdown(
                """
                <div class="panel">
                    <p>Welcome to the campus co-pilot.</p>
                    <p>Add your Gemini API key in the sidebar, then ask a question below.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        for message in st.session_state.messages:
            avatar = "🧑‍🚀" if message["role"] == "user" else "🛰️"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask the campus co-pilot...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🛰️"):
        if not api_key:
            notice = "Please enter a Gemini API key in the sidebar before chatting."
            st.warning(notice)
            st.session_state.messages.append({"role": "assistant", "content": notice})
            return
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            reply = response.text if getattr(response, "text", None) else "No response received."
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as exc:
            error_text = f"Could not reach Gemini right now: {exc}"
            st.error(error_text)
            st.session_state.messages.append({"role": "assistant", "content": error_text})


def main():
    apply_space_theme()
    init_db()

    if "page" not in st.session_state:
        st.session_state.page = "home"

    api_key = render_sidebar()

    if st.session_state.page != "home":
        render_back_button()

    pages = {
        "home": render_home,
        "schedule": render_schedule,
        "tasks": render_tasks,
        "flashcard": render_flashcards,
        "ai": lambda: render_ai(api_key),
    }
    pages.get(st.session_state.page, render_home)()


main()
