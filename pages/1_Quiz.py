import streamlit as st
import random
from pathlib import Path
from datetime import datetime
import database as db

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="QuizMaster - Quiz",
    page_icon="🎮",
    layout="wide"
)

# --------------------------------------------------
# CHECK AUTHENTICATION (PHASE 2)
# --------------------------------------------------
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first!")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# --------------------------------------------------
# DATA FUNCTIONS (PHASE 2 - USING DATABASE)
# --------------------------------------------------
def load_questions():
    """Load questions from DATABASE (Phase 2).
    
    Returns:
        dict: Categories with questions, or empty dict on error
    """
    try:
        categories_list = db.get_all_categories()
        
        categories = {}
        for category in categories_list:
            questions = db.get_questions_by_category(category)
            if questions:
                categories[category] = questions
        
        return categories
            
    except Exception as e:
        st.error(f"⚠️ Error loading questions: {e}")
        return {}

def save_highscore(player_name, category, score, correct_answers, total_questions):
    """Save player's score to DATABASE (Phase 2).
    
    Args:
        player_name: Player's name (username from session)
        category: Quiz category
        score: Total points earned
        correct_answers: Number of correct answers
        total_questions: Total number of questions
    """
    try:
        # Get user_id from session state
        user_id = st.session_state.get('user_id')
        
        if user_id:
            # Save to database
            db.save_score(user_id, category, score, correct_answers, total_questions)
        else:
            st.error("⚠️ User not logged in - score not saved")
            
    except Exception as e:
        st.error(f"⚠️ Error saving highscore: {e}")

# --------------------------------------------------
# GAME LOGIC FUNCTIONS
# --------------------------------------------------
def start_game():
    """Initialize a new quiz game with randomized questions."""
    categories = load_questions()
    selected_category = st.session_state.selected_category
    
    if selected_category and selected_category in categories:
        # Get questions for this category
        questions = categories[selected_category].copy()
        
        # CRITICAL: Randomize question order
        random.shuffle(questions)
        
        # Store shuffled questions in session state
        st.session_state.questions = questions
        st.session_state.game_active = True
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.correct_answers = 0
        st.session_state.answered_current = False
        st.session_state.show_result = False

def check_answer(selected_index, correct_index, points):
    """Check if the selected answer is correct.
    
    Args:
        selected_index: Index of option selected by player
        correct_index: Index of correct option
        points: Points awarded for correct answer
        
    Returns:
        bool: True if answer is correct, False otherwise
    """
    # Mark that current question has been answered
    st.session_state.answered_current = True
    
    # Check if answer is correct
    if selected_index == correct_index:
        st.session_state.score += points
        st.session_state.correct_answers += 1
        return True
    return False

def next_question():
    """Move to next question or end game if no more questions."""
    if st.session_state.current_question < len(st.session_state.questions) - 1:
        # Move to next question
        st.session_state.current_question += 1
        st.session_state.answered_current = False
    else:
        # No more questions - end the game
        end_game()

def end_game():
    """End the quiz and save the score."""
    st.session_state.game_active = False
    st.session_state.show_result = True
    
    # Save highscore to database
    save_highscore(
        player_name=st.session_state.username,
        category=st.session_state.selected_category,
        score=st.session_state.score,
        correct_answers=st.session_state.correct_answers,
        total_questions=len(st.session_state.questions)
    )

# --------------------------------------------------
# UI COMPONENTS
# --------------------------------------------------
def show_question():
    """Display the current question with answer options."""
    questions = st.session_state.questions
    current_idx = st.session_state.current_question
    current_question = questions[current_idx]
    
    # Progress bar
    progress = (current_idx) / len(questions)
    st.progress(progress)
    
    # Question number
    st.write(f"**Question {current_idx + 1} of {len(questions)}**")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Score", st.session_state.score)
    with col2:
        st.metric("✅ Correct", st.session_state.correct_answers)
    with col3:
        st.metric("👤 Player", st.session_state.username)
    
    st.markdown("---")
    
    # Question card
    st.markdown(f"""
        <div style="
            padding: 2rem;
            border-radius: 10px;
            background: #f8f9fa;
            border: 2px solid #667eea;
            margin: 1rem 0;
        ">
            <h3>Question {current_idx + 1}</h3>
            <h2>{current_question['question']}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Difficulty badge
    difficulty = current_question.get('difficulty', 'medium')
    difficulty_colors = {
        'easy': '🟢',
        'medium': '🟡',
        'hard': '🔴'
    }
    st.markdown(f"**Difficulty:** {difficulty_colors.get(difficulty, '⚪')} {difficulty.capitalize()}")
    st.markdown(f"**Points:** {current_question.get('points', 10)}")
    
    st.markdown("---")
    st.markdown("### Choose your answer:")
    
    # Answer options
    options = current_question['options']
    correct_index = current_question['correct']
    
    # Display answer buttons or results
    if not st.session_state.answered_current:
        # Show clickable answer buttons
        for idx, option in enumerate(options):
            button_key = f"option_{current_idx}_{idx}"
            
            if st.button(
                f"{chr(65 + idx)}) {option}",
                key=button_key,
                use_container_width=True
            ):
                # Player clicked an answer - check it
                is_correct = check_answer(idx, correct_index, current_question.get('points', 10))
                st.session_state.last_selected_answer = idx
                st.rerun()
    else:
        # Show results with visual feedback
        last_answer = st.session_state.get('last_selected_answer', -1)
        
        for idx, option in enumerate(options):
            if idx == correct_index:
                # Correct answer - show in green
                st.success(f"✅ {chr(65 + idx)}) {option}")
            elif idx == last_answer:
                # Wrong answer that was selected - show in red
                st.error(f"❌ {chr(65 + idx)}) {option}")
            else:
                # Other options - show normally
                st.write(f"{chr(65 + idx)}) {option}")
        
        st.markdown("---")
        
        # Feedback message
        if last_answer == correct_index:
            st.success("🎉 Correct! Well done!")
            st.balloons()
        else:
            st.error(f"❌ Wrong! The correct answer was: **{options[correct_index]}**")
        
        # Next question button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                next_question()
                st.rerun()

def show_results():
    """Display final quiz results with statistics and action buttons."""
    st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        ">
            <h1>🎉 Quiz Complete!</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate statistics
    total = len(st.session_state.questions)
    correct = st.session_state.correct_answers
    score = st.session_state.score
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏆 Final Score", f"{score} points")
    
    with col2:
        st.metric("✅ Correct Answers", f"{correct}/{total}")
    
    with col3:
        st.metric("📊 Accuracy", f"{percentage:.1f}%")
    
    st.markdown("---")
    
    # Performance message based on percentage
    if percentage >= 90:
        st.success("🌟 Outstanding! You're a true master!")
    elif percentage >= 70:
        st.success("👏 Great job! You really know your stuff!")
    elif percentage >= 50:
        st.info("👍 Good effort! Keep practicing!")
    else:
        st.warning("💪 Don't give up! Practice makes perfect!")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.game_active = False
            st.session_state.show_result = False
            st.switch_page("Home.py")
    
    with col2:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.show_result = False
            start_game()
            st.rerun()
    
    with col3:
        if st.button("🏆 View Highscores", use_container_width=True):
            st.session_state.show_result = False
            st.switch_page("pages/2_Highscores.py")

# --------------------------------------------------
# MAIN PAGE LOGIC
# --------------------------------------------------

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
    </style>
""", unsafe_allow_html=True)

# Check if category is selected
if not st.session_state.get('selected_category'):
    st.warning("⚠️ Please select a category on the Home page!")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# Main page routing
if st.session_state.get('show_result', False):
    # Show results screen
    show_results()
elif not st.session_state.get('game_active', False):
    # Game not started - show start screen
    st.markdown(f"""
        <div class="quiz-header">
            <h1>🎮 {st.session_state.selected_category} Quiz</h1>
            <p>Ready to test your knowledge?</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(f"**Player:** {st.session_state.username}")
    st.write(f"**Category:** {st.session_state.selected_category}")
    
    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        start_game()
        st.rerun()
else:
    # Game is active - show question
    if st.session_state.current_question < len(st.session_state.questions):
        # Header
        st.markdown(f"""
            <div class="quiz-header">
                <h1>🎮 {st.session_state.selected_category} Quiz</h1>
                <p>Answer carefully and earn points!</p>
            </div>
        """, unsafe_allow_html=True)
        
        show_question()
    else:
        # Quiz complete
        end_game()
        st.rerun()

# Sidebar with quiz info
with st.sidebar:
    st.markdown("### 📊 Quiz Progress")
    
    if st.session_state.get('game_active', False):
        st.write(f"**Category:** {st.session_state.selected_category}")
        st.write(f"**Progress:** {st.session_state.current_question + 1}/{len(st.session_state.questions)}")
        st.write(f"**Score:** {st.session_state.score}")
        
        answered_so_far = st.session_state.current_question + (1 if st.session_state.answered_current else 0)
        if answered_so_far > 0:
            accuracy = (st.session_state.correct_answers / answered_so_far) * 100
            st.write(f"**Accuracy:** {accuracy:.0f}%")
        
        st.markdown("---")
        
        if st.button("🚪 Exit Quiz", use_container_width=True):
            st.session_state.game_active = False
            st.session_state.show_result = False
            st.switch_page("Home.py")
