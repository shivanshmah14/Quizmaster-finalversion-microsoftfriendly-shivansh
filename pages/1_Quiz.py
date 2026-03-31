import streamlit as st
import time
import database as db
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="QuizMaster - Quiz",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .quiz-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .question-card {
        padding: 2rem;
        border-radius: 10px;
        background: #f8f9fa;
        border: 2px solid #667eea;
        margin: 1rem 0;
    }
    .correct-answer {
        background-color: #d4edda !important;
        border-color: #28a745 !important;
    }
    .wrong-answer {
        background-color: #f8d7da !important;
        border-color: #dc3545 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ── Guard: must be logged in and have an active game ──────────────────────────
if not st.session_state.get('logged_in', False):
    st.error("⚠️ You must be logged in to play!")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

if not st.session_state.get('game_active', False):
    st.warning("⚠️ No active quiz! Please go to the Home page and select a category.")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

if not st.session_state.get('player_name', ''):
    st.error("⚠️ Player name missing. Please go back to the Home page.")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# ── Ensure answers_given list exists (prevents crash on rerun) ────────────────
if 'answers_given' not in st.session_state:
    st.session_state.answers_given = []

# ── Load questions from SQLite ─────────────────────────────────────────────────
selected_category = st.session_state.selected_category
questions = db.get_questions_by_category(selected_category)

if not questions:
    st.error(f"⚠️ No questions found for category '{selected_category}'. Please ask an admin to add questions.")
    if st.button("🏠 Go to Home"):
        st.session_state.game_active = False
        st.switch_page("Home.py")
    st.stop()

current_q_index = st.session_state.current_question

# ── Quiz complete screen ───────────────────────────────────────────────────────
if current_q_index >= len(questions):
    st.markdown("""
        <div class="quiz-header">
            <h1>🎉 Quiz Complete!</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", f"{st.session_state.score} points")
    with col2:
        st.metric("Correct Answers", f"{st.session_state.correct_answers}/{len(questions)}")
    with col3:
        percentage = (st.session_state.correct_answers / len(questions)) * 100
        st.metric("Percentage", f"{percentage:.1f}%")

    if percentage >= 90:
        st.success("🌟 Outstanding! You're a true master!")
    elif percentage >= 70:
        st.success("👏 Great job! You really know your stuff!")
    elif percentage >= 50:
        st.info("👍 Good effort! Keep practising!")
    else:
        st.warning("💪 Don't give up! Practice makes perfect!")

    # ── Save score to SQLite (not JSON) ───────────────────────────────────────
    if not st.session_state.get('score_saved', False):
        db.save_score(
            user_id=st.session_state.user_id,
            category=selected_category,
            score=st.session_state.score,
            correct_answers=st.session_state.correct_answers,
            total_questions=len(questions)
        )
        st.session_state.score_saved = True

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.game_active = False
            st.session_state.score_saved = False
            st.switch_page("Home.py")
    with col2:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answers_given = []
            st.session_state.correct_answers = 0
            st.session_state.score_saved = False
            st.rerun()
    with col3:
        if st.button("🏆 View Highscores", use_container_width=True):
            st.switch_page("pages/2_Highscores.py")

    st.stop()

# ── Current question ───────────────────────────────────────────────────────────
current_question = questions[current_q_index]

st.markdown(f"""
    <div class="quiz-header">
        <h1>📝 {selected_category} Quiz</h1>
        <p>Question {current_q_index + 1} of {len(questions)}</p>
    </div>
""", unsafe_allow_html=True)

progress = current_q_index / len(questions)
st.progress(progress)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", st.session_state.score)
with col2:
    st.metric("Correct", st.session_state.correct_answers)
with col3:
    st.metric("Player", st.session_state.player_name)

st.markdown("---")

st.markdown(f"""
    <div class="question-card">
        <h3>Question {current_q_index + 1}</h3>
        <h2>{current_question['question']}</h2>
    </div>
""", unsafe_allow_html=True)

difficulty = current_question.get('difficulty', 'medium')
difficulty_colors = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
st.markdown(f"**Difficulty:** {difficulty_colors.get(difficulty, '⚪')} {difficulty.capitalize()}")
st.markdown(f"**Points:** {current_question.get('points', 10)}")

st.markdown("---")
st.markdown("### Choose your answer:")

answer_given_key = f"answer_given_{current_q_index}"
if answer_given_key not in st.session_state:
    st.session_state[answer_given_key] = False

options = current_question['options']
correct_index = current_question['correct']

for idx, option in enumerate(options):
    button_key = f"option_{current_q_index}_{idx}"
    if st.button(
        f"{chr(65 + idx)}) {option}",
        key=button_key,
        use_container_width=True,
        disabled=st.session_state[answer_given_key]
    ):
        st.session_state[answer_given_key] = True
        st.session_state.answers_given.append(idx)

        if idx == correct_index:
            st.session_state.correct_answers += 1
            st.session_state.score += current_question.get('points', 10)
            st.session_state[f"feedback_{current_q_index}"] = "correct"
        else:
            st.session_state[f"feedback_{current_q_index}"] = "wrong"
            st.session_state[f"wrong_index_{current_q_index}"] = idx

        st.rerun()

# ── Feedback after answering ───────────────────────────────────────────────────
if st.session_state[answer_given_key]:
    st.markdown("---")
    feedback = st.session_state.get(f"feedback_{current_q_index}", "")

    if feedback == "correct":
        st.success("✅ Correct! Well done!")
        st.balloons()
    else:
        st.error(f"❌ Wrong! The correct answer was: **{options[correct_index]}**")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➡️ Next Question", use_container_width=True, type="primary"):
            st.session_state.current_question += 1
            st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Quiz Progress")
    st.write(f"**Category:** {selected_category}")
    st.write(f"**Progress:** {current_q_index + 1}/{len(questions)}")
    st.write(f"**Score:** {st.session_state.score}")
    answered_so_far = current_q_index + 1 if st.session_state[answer_given_key] else current_q_index
    if answered_so_far > 0:
        st.write(f"**Accuracy:** {st.session_state.correct_answers}/{answered_so_far}")

    st.markdown("---")
    if st.button("🚪 Exit Quiz", use_container_width=True):
        st.session_state.game_active = False
        st.switch_page("Home.py")