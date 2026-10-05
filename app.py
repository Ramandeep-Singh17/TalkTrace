import streamlit as st
import time
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TalkTrace | Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SAFE CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b0d12;
    }

    section[data-testid="stSidebar"] {
        background-color: #11141b;
    }

    .talktrace-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }

    .talktrace-subtitle {
        color: #8d96a8;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    .brand-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: white;
    }

    .brand-subtitle {
        color: #8d96a8;
        font-size: 0.7rem;
    }

    .card {
        background-color: #12161f;
        border: 1px solid #252b38;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .card-heading {
        color: #9aa4b5;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }

    .status-box {
        background-color: #181d27;
        border: 1px solid #292f3c;
        border-radius: 8px;
        padding: 9px 10px;
        margin-bottom: 7px;
        font-size: 0.78rem;
    }

    .status-done {
        color: #35d07f;
    }

    .status-active {
        color: #62b0ff;
    }

    .status-pending {
        color: #7f8899;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False

if "pipeline_steps" not in st.session_state:
    st.session_state.pipeline_steps = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def update_step(key, state):
    st.session_state.pipeline_steps[key] = state


def get_step_status(key):
    return st.session_state.pipeline_steps.get(key, "pending")


def render_status(icon, label, key):

    status = get_step_status(key)

    if status == "done":
        text = "Done"
        css = "status-done"

    elif status == "active":
        text = "Running..."
        css = "status-active"

    else:
        text = "Pending"
        css = "status-pending"

    st.markdown(
        f"""
        <div class="status-box">
            {icon} <b>{label}</b>
            <span class="{css}" style="float:right;">
                {text}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-title">🎙️ TalkTrace</div>
        <div class="brand-subtitle">
            AI Meeting Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("Meeting Input")

    source = st.text_input(
        "YouTube URL or Local File",
        placeholder="https://youtube.com/watch?v=...",
    )

    language = st.selectbox(
        "Transcript Language",
        ["english", "hinglish"],
    )

    st.divider()

    analyse_button = st.button(
        "🚀 Analyse Meeting",
        use_container_width=True,
        type="primary",
    )

    st.divider()

    st.subheader("Pipeline")

    render_status("🔊", "Audio Processing", "audio")
    render_status("📝", "Transcription", "transcript")
    render_status("🏷️", "Title Generation", "title")
    render_status("📋", "Summarisation", "summary")
    render_status("🔍", "Meeting Extraction", "extract")
    render_status("🧠", "RAG Knowledge Base", "rag")


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="talktrace-title">TalkTrace</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="talktrace-subtitle">'
    'Transcribe · Summarise · Extract · Ask Questions'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# ANALYSIS PIPELINE
# ============================================================

if analyse_button:

    if not source.strip():

        st.warning(
            "Please enter a YouTube URL or local audio/video file."
        )

    else:

        # Reset previous result
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_done = False
        st.session_state.pipeline_steps = {}

        progress = st.empty()

        try:

            # ----------------------------------------------------
            # AUDIO PROCESSING
            # ----------------------------------------------------

            update_step("audio", "active")

            progress.info("🔊 Processing audio...")

            chunks = process_input(source)

            update_step("audio", "done")


            # ----------------------------------------------------
            # TRANSCRIPTION
            # ----------------------------------------------------

            update_step("transcript", "active")

            progress.info("📝 Transcribing meeting...")

            transcript = transcribe_all(
                chunks,
                language,
            )

            update_step("transcript", "done")


            # ----------------------------------------------------
            # TITLE GENERATION
            # ----------------------------------------------------

            update_step("title", "active")

            progress.info("🏷️ Generating meeting title...")

            title = generate_title(transcript)

            update_step("title", "done")


            # ----------------------------------------------------
            # SUMMARY
            # ----------------------------------------------------

            update_step("summary", "active")

            progress.info("📋 Generating meeting summary...")

            summary = summarize(transcript)

            update_step("summary", "done")


            # ----------------------------------------------------
            # EXTRACTION
            # ----------------------------------------------------

            update_step("extract", "active")

            progress.info(
                "🔍 Extracting action items, decisions and questions..."
            )

            action_items = extract_action_items(transcript)

            decisions = extract_key_decisions(transcript)

            questions = extract_questions(transcript)

            update_step("extract", "done")


            # ----------------------------------------------------
            # RAG
            # ----------------------------------------------------

            update_step("rag", "active")

            progress.info("🧠 Building RAG knowledge base...")

            rag_chain = build_rag_chain(transcript)

            update_step("rag", "done")


            # ----------------------------------------------------
            # STORE RESULT
            # ----------------------------------------------------

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }

            st.session_state.pipeline_done = True

            progress.success(
                "✅ Meeting analysis completed successfully!"
            )

            time.sleep(0.5)

            progress.empty()

            st.rerun()


        except Exception as e:

            for key in [
                "audio",
                "transcript",
                "title",
                "summary",
                "extract",
                "rag",
            ]:

                if (
                    st.session_state.pipeline_steps.get(key)
                    == "active"
                ):
                    st.session_state.pipeline_steps[key] = "pending"

            progress.error(
                f"❌ Error: {str(e)}"
            )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.result:

    result = st.session_state.result


    # --------------------------------------------------------
    # SESSION TITLE
    # --------------------------------------------------------

    st.subheader("📌 Meeting Intelligence Report")

    st.markdown(
        f"""
        <div class="card">
            <div class="card-heading">
                Session Title
            </div>
            <div style="
                font-size:1.5rem;
                font-weight:700;
                color:white;
            ">
                {result["title"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # SUMMARY + TRANSCRIPT
    # --------------------------------------------------------

    col1, col2 = st.columns([3, 2])

    with col1:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="card-heading">📋 AI Summary</div>',
            unsafe_allow_html=True,
        )

        st.markdown(result["summary"])

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )


    with col2:

        with st.expander(
            "📝 Full Transcript",
            expanded=False,
        ):

            st.text_area(
                "Transcript",
                result["transcript"],
                height=350,
                label_visibility="collapsed",
            )


    # --------------------------------------------------------
    # MEETING INSIGHTS
    # --------------------------------------------------------

    st.subheader("Meeting Insights")

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="card-heading">✅ Action Items</div>',
            unsafe_allow_html=True,
        )

        st.markdown(result["action_items"])

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )


    with col2:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="card-heading">🔑 Key Decisions</div>',
            unsafe_allow_html=True,
        )

        st.markdown(result["key_decisions"])

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )


    with col3:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="card-heading">❓ Open Questions</div>',
            unsafe_allow_html=True,
        )

        st.markdown(result["open_questions"])

        st.markdown(
            '</div>',
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # RAG CHAT
    # --------------------------------------------------------

    st.divider()

    st.subheader("💬 Ask TalkTrace")

    st.caption(
        "Ask questions about the analysed meeting."
    )


    # Existing chat history

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.write(message["content"])

        else:

            with st.chat_message("assistant"):
                st.write(message["content"])


    # New question

    user_input = st.chat_input(
        "Ask something about the meeting..."
    )


    if user_input:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with st.chat_message("user"):
            st.write(user_input)


        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    answer = ask_question(
                        result["rag_chain"],
                        user_input,
                    )

                    st.write(answer)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as e:

                    error_message = (
                        f"Sorry, I couldn't answer that.\n\n"
                        f"Error: {str(e)}"
                    )

                    st.error(error_message)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                        }
                    )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.write("")
    st.write("")
    st.write("")

    st.title("🎙️ Ready when you are.")

    st.write(
        "Add a YouTube meeting URL or local audio/video file "
        "from the sidebar and click **Analyse Meeting**."
    )

    st.info(
        "TalkTrace can transcribe, summarise, extract meeting "
        "insights and answer questions using RAG."
    )