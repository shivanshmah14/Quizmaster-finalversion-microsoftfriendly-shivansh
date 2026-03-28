import streamlit as st
from pathlib import Path
import pandas as pd
import database as db

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="QuizMaster - Highscores",
    page_icon="🏆",
    layout="wide"
)

# --------------------------------------------------
# CHECK AUTHENTICATION (PHASE 2)
# --------------------------------------------------
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login to view highscores!")
    if st.button("🏠 Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# --------------------------------------------------
# DATA FUNCTIONS (PHASE 2 - USING SQL JOIN)
# --------------------------------------------------
def load_highscores():
    """Load highscores from DATABASE using SQL JOIN (Phase 2).
    
    Uses SQL JOIN to combine scores table with users table
    to get username for each score.
    
    Returns:
        list: List of highscore dictionaries with user info
    """
    try:
        # Use database function with SQL JOIN
        # This joins scores table with users table to get username
        highscores = db.get_highscores(limit=50)
        
        # Convert to format expected by display code
        formatted_scores = []
        for score in highscores:
            formatted_scores.append({
                'player_name': score['username'],  # From JOIN with users table
                'category': score['category'],
                'score': score['score'],
                'correct_answers': score['correct_answers'],
                'total_questions': score['total_questions'],
                'percentage': score['percentage'],
                'date': score['played_at']
            })
        
        return formatted_scores
            
    except Exception as e:
        st.error(f"⚠️ Error loading highscores: {e}")
        return []

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
    <style>
    .highscore-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .trophy {
        font-size: 4rem;
    }
    .rank-1 {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000;
    }
    .rank-2 {
        background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000;
    }
    .rank-3 {
        background: linear-gradient(135deg, #CD7F32, #B87333);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------

# Header
st.markdown("""
    <div class="highscore-header">
        <div class="trophy">🏆</div>
        <h1>Highscores Leaderboard</h1>
        <p>Top performers across all categories</p>
    </div>
""", unsafe_allow_html=True)

# Load highscores
highscores = load_highscores()

# Check if we have any scores
if not highscores:
    st.info("📝 No scores yet! Be the first to complete a quiz!")
    
    if st.button("🏠 Go to Home", use_container_width=True):
        st.switch_page("Home.py")
    st.stop()

# --------------------------------------------------
# FILTER OPTIONS
# --------------------------------------------------
st.markdown("### 🔍 Filter Options")

col1, col2 = st.columns(2)

with col1:
    # Get unique categories from highscores
    categories = list(set([score['category'] for score in highscores]))
    categories.insert(0, "All Categories")
    selected_category = st.selectbox("Category", categories)

with col2:
    # Number of results to display
    display_limit = st.slider("Number of results", 5, 50, 10)

# Filter highscores based on selected category
filtered_scores = highscores
if selected_category != "All Categories":
    filtered_scores = [s for s in highscores if s['category'] == selected_category]

# Limit results
filtered_scores = filtered_scores[:display_limit]

st.markdown("---")

# --------------------------------------------------
# TOP 3 DISPLAY
# --------------------------------------------------
if len(filtered_scores) >= 3:
    st.markdown("### 🥇 Top 3 Players")
    
    for idx, score in enumerate(filtered_scores[:3]):
        rank_class = f"rank-{idx + 1}"
        medal = ["🥇", "🥈", "🥉"][idx]
        
        st.markdown(f"""
            <div class="{rank_class}">
                <h3>{medal} #{idx + 1} - {score['player_name']}</h3>
                <p><strong>Score:</strong> {score['score']} points | 
                   <strong>Category:</strong> {score['category']} | 
                   <strong>Accuracy:</strong> {score['percentage']:.1f}% 
                   ({score['correct_answers']}/{score['total_questions']})</p>
                <p><small>🕐 {score['date']}</small></p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

# --------------------------------------------------
# COMPLETE LEADERBOARD TABLE (USING PANDAS)
# --------------------------------------------------
st.markdown("### 📊 Complete Leaderboard")

if filtered_scores:
    # Convert to pandas DataFrame for better display
    df_data = []
    
    for idx, score in enumerate(filtered_scores):
        df_data.append({
            'Rank': idx + 1,
            'Player': score['player_name'],
            'Category': score['category'],
            'Score': score['score'],
            'Correct': f"{score['correct_answers']}/{score['total_questions']}",
            'Accuracy': f"{score['percentage']:.1f}%",
            'Date': score['date']
        })
    
    # Create DataFrame
    df = pd.DataFrame(df_data)
    
    # Display DataFrame with custom column configuration
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
            "Player": st.column_config.TextColumn("👤 Player", width="medium"),
            "Category": st.column_config.TextColumn("📚 Category", width="medium"),
            "Score": st.column_config.NumberColumn("⭐ Score", width="small"),
            "Correct": st.column_config.TextColumn("✅ Correct", width="small"),
            "Accuracy": st.column_config.TextColumn("📊 Accuracy", width="small"),
            "Date": st.column_config.TextColumn("🕐 Date", width="medium"),
        }
    )

# --------------------------------------------------
# STATISTICS
# --------------------------------------------------
st.markdown("---")
st.markdown("### 📈 Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Scores", len(highscores))

with col2:
    unique_players = len(set([s['player_name'] for s in highscores]))
    st.metric("Unique Players", unique_players)

with col3:
    if highscores:
        avg_score = sum(s['score'] for s in highscores) / len(highscores)
        st.metric("Average Score", f"{avg_score:.0f}")

with col4:
    if highscores:
        highest_score = max(s['score'] for s in highscores)
        st.metric("Highest Score", highest_score)

# --------------------------------------------------
# CATEGORY BREAKDOWN
# --------------------------------------------------
st.markdown("---")
st.markdown("### 📊 Scores by Category")

# Calculate statistics per category
category_data = {}
for score in highscores:
    cat = score['category']
    if cat not in category_data:
        category_data[cat] = {
            'count': 0,
            'total_score': 0,
            'highest': 0
        }
    category_data[cat]['count'] += 1
    category_data[cat]['total_score'] += score['score']
    category_data[cat]['highest'] = max(category_data[cat]['highest'], score['score'])

# Display category statistics
for category, data in category_data.items():
    avg = data['total_score'] / data['count']
    
    with st.expander(f"📚 {category}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Attempts", data['count'])
        
        with col2:
            st.metric("Average Score", f"{avg:.0f}")
        
        with col3:
            st.metric("Highest Score", data['highest'])

# --------------------------------------------------
# PERSONAL BEST SECTION
# --------------------------------------------------
if st.session_state.get('username', ''):
    st.markdown("---")
    st.markdown(f"### 🎯 Your Personal Best - {st.session_state.username}")
    
    # Filter scores for current player
    player_scores = [s for s in highscores if s['player_name'] == st.session_state.username]
    
    if player_scores:
        # Sort by score to get best
        player_scores.sort(key=lambda x: x['score'], reverse=True)
        best_score = player_scores[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Best Score", best_score['score'])
        
        with col2:
            st.metric("Best Accuracy", f"{best_score['percentage']:.1f}%")
        
        with col3:
            st.metric("Total Attempts", len(player_scores))
        
        with col4:
            avg_player_score = sum(s['score'] for s in player_scores) / len(player_scores)
            st.metric("Your Average", f"{avg_player_score:.0f}")
        
        # Display player's recent scores
        st.markdown("#### Your Recent Scores")
        
        player_df_data = []
        for score in player_scores[:5]:  # Show last 5
            player_df_data.append({
                'Category': score['category'],
                'Score': score['score'],
                'Accuracy': f"{score['percentage']:.1f}%",
                'Date': score['date']
            })
        
        if player_df_data:
            player_df = pd.DataFrame(player_df_data)
            st.dataframe(player_df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores yet! Complete a quiz to see your stats here.")

# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")

with col2:
    if st.button("🎮 Start New Quiz", use_container_width=True):
        st.session_state.game_active = False
        st.switch_page("Home.py")
