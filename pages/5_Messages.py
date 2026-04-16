import streamlit as st
import database as db

st.set_page_config(page_title="QuizMaster - Messages", page_icon="💬", layout="wide")

if not st.session_state.get("logged_in", False):
    st.warning("Please login first!")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

st.markdown("""
    <div style="text-align:center; padding:2rem;
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    border-radius:10px; color:white; margin-bottom:2rem;">
        <h1>💬 Messages</h1>
        <p>Send a direct message by username</p>
    </div>
""", unsafe_allow_html=True)


def safe_get_user_by_username(username):
    if hasattr(db, "get_user_by_username"):
        return db.get_user_by_username(username)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def safe_send_message(sender_id, receiver_id, message, category=None):
    if hasattr(db, "send_message"):
        return db.send_message(sender_id, receiver_id, message, category)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            category TEXT,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """
    )
    cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, category, message) VALUES (?, ?, ?, ?)",
        (sender_id, receiver_id, category, message),
    )
    conn.commit()
    conn.close()


def safe_get_messages_for_user(user_id, limit=100):
    if hasattr(db, "get_messages_for_user"):
        return db.get_messages_for_user(user_id, limit=limit)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            category TEXT,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """
    )
    cursor.execute(
        """
        SELECT
            m.id,
            m.category,
            m.message,
            m.sent_at,
            sender.username AS sender_username,
            receiver.username AS receiver_username
        FROM messages m
        JOIN users sender ON m.sender_id = sender.id
        JOIN users receiver ON m.receiver_id = receiver.id
        WHERE m.receiver_id = ?
        ORDER BY m.sent_at DESC
        LIMIT ?
    """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def safe_get_all_messages(limit=500):
    if hasattr(db, "get_all_messages"):
        return db.get_all_messages(limit=limit)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            category TEXT,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """
    )
    cursor.execute(
        """
        SELECT
            m.id,
            m.category,
            m.message,
            m.sent_at,
            sender.username AS sender_username,
            receiver.username AS receiver_username
        FROM messages m
        JOIN users sender ON m.sender_id = sender.id
        JOIN users receiver ON m.receiver_id = receiver.id
        ORDER BY m.sent_at DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


tab1, tab2, tab3 = st.tabs(["Send Message", "Inbox", "Sent"])

with tab1:
    st.subheader("Send Message to Any User")
    st.caption("Type the exact username of the user you want to message.")

    with st.form("send_message_by_username_form"):
        target_username = st.text_input("Recipient Username")
        category = st.text_input("Category (optional)")
        message_text = st.text_area("Message", placeholder="Great quiz! I loved it.")
        submit = st.form_submit_button("Send Message", use_container_width=True)

        if submit:
            if not target_username.strip() or not message_text.strip():
                st.error("Please enter both recipient username and message.")
            elif target_username.strip().lower() == st.session_state.get("username", "").lower():
                st.error("You cannot send a message to yourself.")
            else:
                receiver = safe_get_user_by_username(target_username.strip())
                sender_id = st.session_state.get("user_id")
                if not receiver:
                    st.error("That username does not exist.")
                elif not sender_id:
                    st.error("Your session is missing user info. Please login again.")
                else:
                    safe_send_message(
                        sender_id=sender_id,
                        receiver_id=receiver["id"],
                        message=message_text.strip(),
                        category=category.strip() or None,
                    )
                    st.success(f"Message sent to {receiver['username']}.")

with tab2:
    st.subheader("Inbox")
    inbox = safe_get_messages_for_user(st.session_state.get("user_id"), limit=100)
    if not inbox:
        st.info("No messages yet.")
    else:
        for msg in inbox:
            category_label = msg["category"] if msg.get("category") else "General"
            st.markdown(
                f"**From:** {msg['sender_username']}  \n"
                f"**Category:** {category_label}  \n"
                f"**Sent:** {msg['sent_at']}"
            )
            st.write(msg["message"])
            st.markdown("---")

with tab3:
    st.subheader("Sent")
    all_messages = safe_get_all_messages(limit=500)
    my_username = st.session_state.get("username")
    sent = [m for m in all_messages if m.get("sender_username") == my_username]
    if not sent:
        st.info("You have not sent any messages yet.")
    else:
        for msg in sent:
            category_label = msg["category"] if msg.get("category") else "General"
            st.markdown(
                f"**To:** {msg['receiver_username']}  \n"
                f"**Category:** {category_label}  \n"
                f"**Sent:** {msg['sent_at']}"
            )
            st.write(msg["message"])
            st.markdown("---")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("Go to Categories", use_container_width=True):
        st.switch_page("pages/3_Categories.py")
