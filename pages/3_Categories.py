import streamlit as st
import database as db

st.set_page_config(page_title="QuizMaster - Categories", page_icon="📚", layout="wide")

if not st.session_state.get('logged_in', False):
    st.warning("Please login to view categories!")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

def load_questions():
    try:
        categories_list = db.get_all_categories()
        categories = {}
        for category in categories_list:
            questions = db.get_questions_by_category(category)
            if questions:
                categories[category] = questions
        return categories
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return {}

st.markdown("""
    <style>
    .categories-header {
        text-align:center; padding:2rem;
        background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
        border-radius:10px; color:white; margin-bottom:2rem;
    }
    .easy   { background-color:#d4edda; color:#155724; display:inline-block; padding:0.25rem 0.75rem; border-radius:15px; font-size:0.85rem; font-weight:bold; margin:0.25rem; }
    .medium { background-color:#fff3cd; color:#856404; display:inline-block; padding:0.25rem 0.75rem; border-radius:15px; font-size:0.85rem; font-weight:bold; margin:0.25rem; }
    .hard   { background-color:#f8d7da; color:#721c24; display:inline-block; padding:0.25rem 0.75rem; border-radius:15px; font-size:0.85rem; font-weight:bold; margin:0.25rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="categories-header">
        <h1>Quiz Categories</h1>
        <p>Explore all available quiz topics and questions</p>
    </div>
""", unsafe_allow_html=True)

categories = load_questions()

if not categories:
    st.warning("No categories available yet!")
    if st.session_state.get('is_admin', False):
        st.info("As an admin, you can add questions in the Admin Panel!")
        if st.button("Go to Admin Panel"):
            st.switch_page("pages/4_Admin.py")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

st.markdown("### Overview")
col1, col2, col3 = st.columns(3)
total_questions = sum(len(qs) for qs in categories.values())
with col1:
    st.metric("Total Categories", len(categories))
with col2:
    st.metric("Total Questions", total_questions)
with col3:
    st.metric("Avg per Category", f"{total_questions/len(categories):.1f}")

st.markdown("---")

for category_name, questions in categories.items():
    with st.expander(f"{category_name} ({len(questions)} questions)", expanded=False):
        diff_counts = {'easy': 0, 'medium': 0, 'hard': 0}
        total_points = 0
        for q in questions:
            diff_counts[q.get('difficulty', 'medium')] = diff_counts.get(q.get('difficulty', 'medium'), 0) + 1
            total_points += q.get('points', 10)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Questions", len(questions))
        with col2:
            st.metric("Easy", diff_counts['easy'])
        with col3:
            st.metric("Medium", diff_counts['medium'])
        with col4:
            st.metric("Hard", diff_counts['hard'])

        st.write(f"**Total Points Available:** {total_points}")
        st.markdown("---")
        st.markdown("#### Questions Preview")

        for idx, question in enumerate(questions):
            st.markdown(f"**Question {idx + 1}**")
            st.write(question['question'])
            diff = question.get('difficulty', 'medium')
            st.markdown(
                f"<span class='{diff}'>{diff.upper()}</span> "
                f"<span style='color:#666;'>{question.get('points', 10)} points</span>",
                unsafe_allow_html=True
            )
            for opt_idx, option in enumerate(question['options']):
                if opt_idx == question['correct']:
                    st.success(f"{chr(65+opt_idx)}) {option} (Correct)")
                else:
                    st.write(f"{chr(65+opt_idx)}) {option}")
            if idx < len(questions) - 1:
                st.markdown("---")

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"Start {category_name} Quiz", key=f"start_{category_name}", use_container_width=True):
                st.session_state.selected_category = category_name
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.game_active = True
                st.session_state.answers_given = []
                st.session_state.correct_answers = 0
                st.session_state.answered_current = False
                st.session_state.show_result = False
                st.switch_page("pages/1_Quiz.py")

st.markdown("---")
st.markdown("### Difficulty Distribution")
all_diffs = [q.get('difficulty', 'medium') for qs in categories.values() for q in qs]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Easy", all_diffs.count('easy'))
with col2:
    st.metric("Medium", all_diffs.count('medium'))
with col3:
    st.metric("Hard", all_diffs.count('hard'))

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("View Highscores", use_container_width=True):
        st.switch_page("pages/2_Highscores.py")