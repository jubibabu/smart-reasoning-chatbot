import streamlit as st
from reasoning_engine import query_gemini, format_confidence_emoji

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Reasoning Chatbot",
    page_icon="🧠",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .step-card {
        background: #1e1e2e;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .step-number {
        font-size: 0.75rem;
        color: #667eea;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .step-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e0e0e0;
        margin: 0.2rem 0;
    }
    .answer-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #667eea55;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #f0f0f0;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #667eea22;
        color: #a89cff;
        border: 1px solid #667eea55;
    }
    .history-item {
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.4rem;
        cursor: pointer;
        transition: background 0.2s;
        font-size: 0.9rem;
        color: #ccc;
        background: #ffffff08;
        border: 1px solid #ffffff10;
    }
    .divider {
        border: none;
        border-top: 1px solid #ffffff15;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, main_col = st.columns([1, 2.8], gap="large")

# ── Sidebar: History ───────────────────────────────────────────────────────────
with left_col:
    st.markdown("### 🧠 Smart Reasoning")
    st.markdown("<div class='subtitle'>Step-by-step AI thinking</div>", unsafe_allow_html=True)

    st.markdown("**Example questions**")
    examples = [
        "Should I learn Python or JavaScript first?",
        "How does photosynthesis work?",
        "What's the best way to study for exams?",
        "Explain how the internet works",
        "Why is the sky blue?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state.current_question = ex

    if st.session_state.history:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("**Recent questions**")
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            short = item["question"][:45] + "..." if len(item["question"]) > 45 else item["question"]
            if st.button(f"↩ {short}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_result = item["result"]
                st.session_state.current_question = item["question"]

# ── Main panel ─────────────────────────────────────────────────────────────────
with main_col:
    st.markdown("<div class='main-title'>Smart Reasoning Chatbot</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Ask anything — watch the AI break it down step by step</div>", unsafe_allow_html=True)

    # Input
    question = st.text_area(
        "Your question",
        value=st.session_state.current_question,
        placeholder="e.g. Should I use SQL or NoSQL for my app?",
        height=90,
        label_visibility="collapsed"
    )

    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        ask_clicked = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear", use_container_width=False):
            st.session_state.current_result = None
            st.session_state.current_question = ""
            st.rerun()

    # ── Process question ───────────────────────────────────────────────────────
    if ask_clicked and question.strip():
        with st.spinner("Thinking step by step..."):
            try:
                result = query_gemini(question.strip())
                st.session_state.current_result = result
                st.session_state.current_question = question.strip()
                st.session_state.history.append({
                    "question": question.strip(),
                    "result": result
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure your ANTHROPIC_API_KEY is set in your .env file.")

    # ── Display result ─────────────────────────────────────────────────────────
    if st.session_state.current_result:
        res = st.session_state.current_result

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Problem breakdown
        with st.expander("📋 Problem breakdown", expanded=True):
            for i, part in enumerate(res.get("problem_breakdown", []), 1):
                st.markdown(f"**{i}.** {part}")

        st.markdown("")

        # Reasoning steps
        st.markdown("#### 🔍 Reasoning trace")
        for step in res.get("reasoning_steps", []):
            with st.expander(
                f"Step {step.get('step', '?')} — {step.get('title', 'Untitled')}",
                expanded=True
            ):
                st.markdown(f"**💭 Thinking:** {step.get('thinking', '')}")
                st.markdown(f"**✅ Result:** {step.get('result', '')}")

        st.markdown("")

        # Final answer
        st.markdown("#### 💡 Final answer")
        st.markdown(
            f"<div class='answer-box'>{res.get('final_answer', '')}</div>",
            unsafe_allow_html=True
        )

        st.markdown("")

        # Why it makes sense + confidence
        col_a, col_b = st.columns([3, 1])
        with col_a:
            with st.expander("🤔 Why this answer makes sense"):
                st.markdown(res.get("why_it_makes_sense", ""))
        with col_b:
            conf = res.get("confidence", "medium")
            st.markdown("**Confidence**")
            st.markdown(f"<div class='badge'>{format_confidence_emoji(conf)}</div>", unsafe_allow_html=True)

    else:
        # Empty state
        st.markdown("""
        <div style='text-align:center; padding: 4rem 2rem; color: #555;'>
            <div style='font-size: 3rem; margin-bottom: 1rem'>🧠</div>
            <div style='font-size: 1.1rem; font-weight: 600; color: #888'>Ask a question to see step-by-step reasoning</div>
            <div style='font-size: 0.9rem; margin-top: 0.5rem; color: #555'>
                Try an example from the left panel, or type your own question above
            </div>
        </div>
        """, unsafe_allow_html=True)
