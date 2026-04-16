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


def get_creator_name(user_id):
    if not user_id:
        return "System"
    user = db.get_user_by_id(user_id)
    if user and user.get("username"):
        return user["username"]
    return "Unknown"

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

st.markdown("### Create a Public Quiz Question")
st.caption("Any logged-in user can add questions. Added questions are visible and playable by everyone.")

with st.form("create_public_question_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_category = st.text_input("Category Name")
        new_difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
    with col2:
        points_map = {"easy": 10, "medium": 15, "hard": 20}
        new_points = st.number_input("Points", min_value=1, max_value=100, value=points_map[new_difficulty])

    new_question = st.text_area("Question", height=100)
    st.markdown("Answer Options")
    new_opt_a = st.text_input("Option A")
    new_opt_b = st.text_input("Option B")
    new_opt_c = st.text_input("Option C")
    new_opt_d = st.text_input("Option D")
    new_correct = st.radio("Correct Answer", ["A", "B", "C", "D"], horizontal=True)

    create_submit = st.form_submit_button("Add Public Question", use_container_width=True)
    if create_submit:
        required = [new_category, new_question, new_opt_a, new_opt_b, new_opt_c, new_opt_d]
        if not all(required):
            st.error("Please fill in all fields before submitting.")
        else:
            db.add_question(
                category=new_category.strip(),
                question=new_question.strip(),
                options=[new_opt_a.strip(), new_opt_b.strip(), new_opt_c.strip(), new_opt_d.strip()],
                correct_index=ord(new_correct) - ord("A"),
                difficulty=new_difficulty,
                points=int(new_points),
                created_by=st.session_state.get("user_id"),
            )
            st.success(f"Question added to '{new_category.strip()}'. Everyone can now play it.")
            st.rerun()

st.markdown("---")

st.markdown("### Send Message to Any User")
all_targets = db.get_all_usernames(exclude_user_id=st.session_state.get("user_id"))
if all_targets:
    with st.form("dm_any_user_form"):
        dm_any_target = st.selectbox("Select user", all_targets)
        dm_any_category = st.text_input("Category (optional)", placeholder="e.g. Science")
        dm_any_text = st.text_area("Message", placeholder="Hey! Nice quiz.")
        dm_any_submit = st.form_submit_button("Send DM", use_container_width=True)
        if dm_any_submit:
            if not dm_any_text.strip():
                st.error("Please type a message first.")
            else:
                receiver = db.get_user_by_username(dm_any_target)
                sender_id = st.session_state.get("user_id")
                if receiver and sender_id:
                    db.send_message(
                        sender_id=sender_id,
                        receiver_id=receiver["id"],
                        message=dm_any_text.strip(),
                        category=dm_any_category.strip() or None,
                    )
                    st.success(f"Message sent to {dm_any_target}.")
                    st.rerun()
                else:
                    st.error("Could not send message to this user.")
else:
    st.caption("No other users found yet. Ask someone to create an account first.")

st.markdown("---")

st.markdown("### My Messages")
my_messages = db.get_messages_for_user(st.session_state.get("user_id"), limit=20)
if my_messages:
    for msg in my_messages:
        category_label = msg["category"] if msg.get("category") else "General"
        st.info(
            f"From **{msg['sender_username']}** about **{category_label}**\n\n"
            f"{msg['message']}\n\n"
            f"_Sent: {msg['sent_at']}_"
        )
else:
    st.caption("No messages yet.")

st.markdown("---")

for category_name, questions in categories.items():
    category_creators = db.get_category_creators(category_name)
    creator_label = ", ".join(category_creators)
    with st.expander(f"{category_name} ({len(questions)} questions) • By: {creator_label}", expanded=False):
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
        st.write(f"**Created by:** {creator_label}")
        st.markdown("---")
        st.markdown("#### Message the Quiz Creator")
        dm_targets = [
            username for username in category_creators
            if username not in {"System", st.session_state.get("username")}
        ]
        if dm_targets:
            target = st.selectbox(
                "Select creator",
                dm_targets,
                key=f"dm_target_{category_name}",
            )
            dm_text = st.text_area(
                "Message",
                placeholder="Great quiz! I loved it.",
                key=f"dm_text_{category_name}",
            )
            if st.button("Send Message", key=f"dm_send_{category_name}", use_container_width=True):
                if not dm_text.strip():
                    st.error("Please type a message first.")
                else:
                    receiver = db.get_user_by_username(target)
                    sender_id = st.session_state.get("user_id")
                    if receiver and sender_id:
                        db.send_message(
                            sender_id=sender_id,
                            receiver_id=receiver["id"],
                            message=dm_text.strip(),
                            category=category_name,
                        )
                        st.success(f"Message sent to {target}.")
                    else:
                        st.error("Could not send message to this user.")
        else:
            st.caption("No creator account available to message for this category.")
        st.markdown("---")
        st.markdown("#### Questions Preview")

        for idx, question in enumerate(questions):
            st.markdown(f"**Question {idx + 1}**")
            st.write(question['question'])
            st.markdown(f"**Created by:** `{get_creator_name(question.get('created_by'))}`")
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
