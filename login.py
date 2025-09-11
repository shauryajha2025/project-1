import streamlit as st
import re
import hashlib
import sqlite3
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Capital Compass",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply dark theme CSS
def apply_dark_theme():
    st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stTextInput>div>div>input, .stTextInput>div>div>input:focus {
        background-color: #262730;
        color: #fafafa;
        border-color: #4a4a4a;
    }
    .stButton>button {
        background-color: #4a4a4a;
        color: #fafafa;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #5a5a5a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .success {
        color: #4caf50;
        font-weight: bold;
    }
    .error {
        color: #f44336;
        font-weight: bold;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .compass-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #7e7e7e;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

apply_dark_theme()

# Database setup
def init_db():
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Password validation
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return "Password must contain at least one special character"
    return None

# User registration
def register_user(username, password):
    conn = sqlite3.connect('capital_compass.db')
    c = conn.cursor()
    
    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return "Username already exists"
    
    # Hash password and store user
    password_hash = hash_password(password)
    c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
              (username, password_hash))
    conn.commit()
    conn.close()
    return None

# Main application
def main():
    # Header section
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown('<div class="compass-icon">🧭</div>', unsafe_allow_html=True)
    st.title("Capital Compass")
    st.subheader("Navigate Your Financial Future")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialize database
    init_db()
    
    # Registration form
    with st.form("registration_form"):
        st.markdown("### Create Your Account")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", 
                                placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", 
                                        placeholder="Re-enter your password")
        
        # Terms and conditions
        agree = st.checkbox("I agree to the Terms and Conditions")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # Validate inputs
            if not username:
                st.error("Username is required", icon="🚨")
            elif len(username) < 4:
                st.error("Username must be at least 4 characters long", icon="🚨")
            elif not password:
                st.error("Password is required", icon="🚨")
            elif password != confirm_password:
                st.error("Passwords do not match", icon="🚨")
            elif not agree:
                st.error("You must agree to the Terms and Conditions", icon="🚨")
            else:
                # Validate password strength
                password_error = validate_password(password)
                if password_error:
                    st.error(password_error, icon="🚨")
                else:
                    # Register user
                    error = register_user(username, password)
                    if error:
                        st.error(error, icon="🚨")
                    else:
                        st.success("Account created successfully! You can now log in.", icon="✅")
                        # Reset form
                        st.experimental_rerun()
    
    # Password guidelines
    with st.expander("Password Requirements"):
        st.write("""
        - At least 8 characters long
        - Contains at least one uppercase letter (A-Z)
        - Contains at least one lowercase letter (a-z)
        - Contains at least one number (0-9)
        - Contains at least one special character (!@#$%^&* etc.)
        """)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("© 2023 Capital Compass • All Rights Reserved")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
