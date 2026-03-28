import streamlit as st
import database as db

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="QuizMaster - Admin Panel",
    page_icon="⚙️",
    layout="wide"
)

# --------------------------------------------------
# CHECK AUTHENTICATION AND ADMIN STATUS
# --------------------------------------------------
if not st.session_state.get('logged_in', False):
    st.error("🔒 Please login first")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

if not st.session_state.get('is_admin', False):
    st.error("🚫 Access Denied: Admin privileges required")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
    <style>
    .admin-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .question-card {
        padding: 1rem;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Admin Panel</h1>
        <p>Manage Questions & Quiz Content</p>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TABS FOR DIFFERENT ADMIN FUNCTIONS
# --------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Question", "✏️ Edit Questions", "📊 Statistics", "🔄 Migrate JSON"])

# --------------------------------------------------
# TAB 1: ADD NEW QUESTION
# --------------------------------------------------
with tab1:
    st.header("➕ Add New Question")
    
    with st.form("add_question_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.text_input(
                "Category",
                help="Enter existing category or create new one"
            )
            difficulty = st.selectbox(
                "Difficulty",
                ["easy", "medium", "hard"]
            )
        
        with col2:
            # Auto-set points based on difficulty
            points_map = {"easy": 10, "medium": 15, "hard": 20}
            points = st.number_input(
                "Points",
                min_value=1,
                max_value=100,
                value=points_map[difficulty]
            )
        
        question_text = st.text_area(
            "Question",
            height=100,
            help="Enter the question text"
        )
        
        st.subheader("Answer Options")
        option_a = st.text_input("Option A")
        option_b = st.text_input("Option B")
        option_c = st.text_input("Option C")
        option_d = st.text_input("Option D")
        
        correct_answer = st.radio(
            "Correct Answer",
            ["A", "B", "C", "D"],
            horizontal=True
        )
        
        submit = st.form_submit_button("Add Question", use_container_width=True)
        
        if submit:
            if not all([category, question_text, option_a, option_b, option_c, option_d]):
                st.error("❌ Please fill in all fields")
            else:
                options = [option_a, option_b, option_c, option_d]
                correct_index = ord(correct_answer) - ord('A')
                
                question_id = db.add_question(
                    category=category,
                    question=question_text,
                    options=options,
                    correct_index=correct_index,
                    difficulty=difficulty,
                    points=points,
                    created_by=st.session_state.user_id
                )
                
                st.success(f"✅ Question added successfully! (ID: {question_id})")
                st.balloons()

# --------------------------------------------------
# TAB 2: EDIT/DELETE QUESTIONS
# --------------------------------------------------
with tab2:
    st.header("✏️ Edit or Delete Questions")
    
    # Category filter
    categories = db.get_all_categories()
    
    if categories:
        selected_cat = st.selectbox("Select Category", categories)
        
        # Get questions for selected category
        questions = db.get_questions_by_category(selected_cat)
        
        if questions:
            st.write(f"**{len(questions)} questions found in {selected_cat}**")
            
            for q in questions:
                with st.expander(f"Q{q['id']}: {q['question'][:60]}..."):
                    st.markdown(f"**Full Question:** {q['question']}")
                    st.write(f"**Difficulty:** {q['difficulty']} | **Points:** {q['points']}")
                    
                    st.write("**Options:**")
                    for idx, opt in enumerate(q['options']):
                        prefix = "✅" if idx == q['correct'] else "  "
                        st.write(f"{prefix} {chr(65+idx)}) {opt}")
                    
                    st.markdown("---")
                    
                    # Edit form
                    with st.form(f"edit_form_{q['id']}"):
                        st.subheader("Edit Question")
                        
                        new_question = st.text_area("Question", value=q['question'], key=f"q_{q['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_difficulty = st.selectbox(
                                "Difficulty",
                                ["easy", "medium", "hard"],
                                index=["easy", "medium", "hard"].index(q['difficulty']),
                                key=f"diff_{q['id']}"
                            )
                        with col2:
                            new_points = st.number_input(
                                "Points",
                                value=q['points'],
                                key=f"pts_{q['id']}"
                            )
                        
                        new_opt_a = st.text_input("Option A", value=q['options'][0], key=f"a_{q['id']}")
                        new_opt_b = st.text_input("Option B", value=q['options'][1], key=f"b_{q['id']}")
                        new_opt_c = st.text_input("Option C", value=q['options'][2], key=f"c_{q['id']}")
                        new_opt_d = st.text_input("Option D", value=q['options'][3], key=f"d_{q['id']}")
                        
                        new_correct = st.radio(
                            "Correct Answer",
                            ["A", "B", "C", "D"],
                            index=q['correct'],
                            horizontal=True,
                            key=f"corr_{q['id']}"
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                new_options = [new_opt_a, new_opt_b, new_opt_c, new_opt_d]
                                new_correct_idx = ord(new_correct) - ord('A')
                                
                                success = db.update_question(
                                    question_id=q['id'],
                                    question=new_question,
                                    options=new_options,
                                    correct_index=new_correct_idx,
                                    difficulty=new_difficulty,
                                    points=new_points
                                )
                                
                                if success:
                                    st.success("✅ Question updated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Update failed")
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete Question", use_container_width=True, type="secondary"):
                                if db.delete_question(q['id']):
                                    st.success("✅ Question deleted!")
                                    st.rerun()
                                else:
                                    st.error("❌ Deletion failed")
        else:
            st.info("No questions found in this category")
    else:
        st.warning("No categories found. Add questions first!")

# --------------------------------------------------
# TAB 3: STATISTICS
# --------------------------------------------------
with tab3:
    st.header("📊 Database Statistics")
    
    categories = db.get_all_categories()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Categories", len(categories))
    
    with col2:
        total_q = sum(len(db.get_questions_by_category(cat)) for cat in categories)
        st.metric("Total Questions", total_q)
    
    with col3:
        # Get user count
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        conn.close()
        st.metric("Total Users", user_count)
    
    st.markdown("---")
    
    # Category breakdown
    st.subheader("Questions by Category")
    
    for cat in categories:
        questions = db.get_questions_by_category(cat)
        
        # Count difficulties
        diff_counts = {"easy": 0, "medium": 0, "hard": 0}
        total_points = 0
        
        for q in questions:
            diff_counts[q['difficulty']] += 1
            total_points += q['points']
        
        with st.expander(f"📚 {cat} ({len(questions)} questions)"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🟢 Easy", diff_counts['easy'])
            with col2:
                st.metric("🟡 Medium", diff_counts['medium'])
            with col3:
                st.metric("🔴 Hard", diff_counts['hard'])
            with col4:
                st.metric("Total Points", total_points)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Scores")
    recent_scores = db.get_highscores(limit=10)
    
    if recent_scores:
        for score in recent_scores:
            st.write(f"**{score['username']}** - {score['category']} - {score['score']} points ({score['percentage']:.1f}%)")
    else:
        st.info("No scores recorded yet")

# --------------------------------------------------
# TAB 4: MIGRATE FROM JSON
# --------------------------------------------------
with tab4:
    st.header("🔄 Migrate Questions from JSON")
    
    st.info("""
    **Migration Tool**: Import questions from your existing `questions.json` file into the database.
    
    ⚠️ **Warning**: This will add questions to the database. Duplicate questions may be created if run multiple times.
    """)
    
    json_path = st.text_input(
        "JSON File Path",
        value="data/questions.json",
        help="Path to your questions.json file"
    )
    
    if st.button("🔄 Start Migration", type="primary"):
        try:
            from pathlib import Path
            path = Path(json_path)
            
            if not path.exists():
                st.error(f"❌ File not found: {json_path}")
            else:
                count = db.migrate_json_to_db(path)
                st.success(f"✅ Successfully migrated {count} questions!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Migration failed: {e}")

# --------------------------------------------------
# SIDEBAR - QUICK ACTIONS
# --------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Admin Panel")
    st.write(f"**Admin:** {st.session_state.username}")
    
    st.markdown("---")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    if st.button("🏆 View Highscores", use_container_width=True):
        st.switch_page("pages/2_Highscores.py")
